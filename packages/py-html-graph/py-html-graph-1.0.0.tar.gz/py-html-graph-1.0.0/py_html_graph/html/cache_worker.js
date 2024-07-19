self.importScripts('data:application/javascript;base64,' + '$jtc.py-html-graph.inside.httpjs$');
/* 通信协议: 
   1. main_to_worker_signal 用于 主线程向 worker 发送信号, worker_to_main_signal 用于 worker 向主
      线程发送信号, signal 非 0 即代表有信号, 每次接收到信号之后, 要把 对方的 signal 设置成 0
   2. main_to_worker -1 用于初次的配对, 仅测试是否能成功通信, 不含有实际信息, worker 需要回复 signal -1
   3. main_to_worker -2 用于初始化, 获取基本信息, 比如 最大值、最小值, worker 回复 -2
   4. main_to_worker 负的其它值, 用于实际获取数据 (值是json字符串长度的相反数), worker 回复 bytes 长
      度 (一定大于0) 
   5. main_to_worker 10000~20000, 用于传输鼠标位置, 就用这个值表示, 没有其它数据, 10000 代表在最左边, 
      20000 表示在最右边, worker 需要回复 1
   6. main_to_worker 1 用于输出 worker 的统计信息, worker 自身输出, 不反回, 没有返回数据, worker 回复 1
   7. 创建时 主线程需要postMessage 共享的 arraybuffer, worker postMessage仅告知主线程创建成功
   8. 主线程中修改了 signal 之后需要调用 Atomics.notify, worker中修改了不用, 主线程通过 while 循环获取
   9. shared_bytes 用于 worker 向主线程传回结果, 和主线程中输入命令, 主线程会写入 json 字符串, 
      worker 写入二进制数据, 在当前协议下, 不会同时写入或读取, 不需要用 Atomics
*/

/** 缓存策略:
 *  1. 整体上缩放的优先级要高于左右移动, 缩放明显可以比左右移动更快
 *  2. 小于一定大小的前几个 level, 全部缓存
 *  3. 需要将每一个 level 每一个区域的数据根据与当前显示区域的"距离" (到达那需要操作的时间) 进行划分等级, 
 *     距离越近, 等级越低, 优先级越高
 *  4. 在一定等级 (暂定常数A) 以内, 如果没有就要缓存, 在一定等级之内 (暂定常数B), 有了不会删, 但是不会去单独缓存,
 *     超过B等级, 就会删除
 *  5. 缓存的数据库是一个字典, key 为 level, value: 一个数组, 范围是当前请求所有的 UNCNECESSARY 范围,
 *     创建时是空白的, 收到数据后在对应的位置写入, 并且还有一个 uint8array (每个数据点只占一个字节) 记录状态
 *  6. 上述的数组, 都是连续的二进制数据, 储存 float32, 就是 4 字节, 使用 Uint8Array
 *  7. 目前不会对同一批次中需要缓存的数据做优先级区分, 目前使用 http 请求, 将来可能会使用 websocket, 并进行优先级
 *     区分
 *  8. 每次请求数据, 如果缓存中有, 直接返回, 如果没有, 发送一个阻塞的 http 请求, 获取当前数据
 */

/** 缓存更新流程:
 *  一、针对用户请求新的数据 (即图表范围变化或鼠标移动)
 *  1. 每次请求之后, 重新计算整个缓存范围 (包括 required 和 unnecessary), 这时需同时保留旧的和新的
 *  2. 根据新旧缓存范围的变化, 移动 cached_data 中的数据 (主要是使index匹配)
 *  3. 检查 cached_data 中, 属于 required 但是状态为 FREE 的, 发出 http 请求, 并将状态改为 REQUESTING
 *     这里通过一个一个遍历 cached_data 中状态的 uint8array 实现, 整理出不同的连续范围
 * 
 *  二、针对每次收到 http 请求的数据
 *  1. 如果成功 (200), 根据缓存的范围, 将数据写入对应的位置, 并将状态改为 LOADED, 超出 UNNECESSARY 范围的丢弃
 *  2. 如果失败 (timeout error 非200), 把对应区域的状态标记为 FREE, 对该level重新进行 一(3) 的流程
 */

const CACHE_LOADED = 1;
const CACHE_REQUESTING = 2;
const CACHE_FREE = 0; // new Uint8Array 创建时默认就是 0

var required_cache_area = {}; // key 为 level, value 为 {start: xxx, end: xxx}
var unnecessary_cache_area = {}; // key 为 level, value 为 {start: xxx, end: xxx}
var cached_data = {};
var whole_level_caches = {};
var shared_bytes = null; // 长度为 1MB, Uint8Array
var main_to_worker_signal = null; // 长度为 4, Int32Array
var worker_to_main_signal = null; // 长度为 4, Int32Array
var BASE_URL; // 获取数据的链接
var TOTAL_DATA_POINTS;
var VARIABLE_NUM;

const MAX_CACHE_ALL_SIZE = '$jtc.py-html-graph.max-whole-level-cache-size$'; // user-configurable
var MAX_LEVEL = -1;
var MAX_CACHE_ALL_LEVEL = -1;

var current_request_start = -1;
var current_request_end = -1;
var current_request_step = -1;
var current_request_level = -1;
var current_window_max = -1;
var has_request = false;
var mouse_position = 0.5;
var current_request_promise_resolve = null;

var ongoing_requests = new Set();


var do_whole_level_cache = async () => {
    var current = MAX_LEVEL;
    for (; ;) {
        if (current < MAX_CACHE_ALL_LEVEL) {
            break;
        }
        var i = current;
        var step = Math.pow(2, i);
        var start, end;
        if (i == 0) {
            start = 0;
            end = TOTAL_DATA_POINTS;
        } else {
            start = - step / 2;
            end = fix_up_with_remainder(TOTAL_DATA_POINTS, step, step / 2) + 1;
        }
        var json_data = {
            start: start,
            end: end,
            step: step
        };
        json_data = stringToHex(JSON.stringify(json_data));
        var url = BASE_URL + '/' + json_data;
        var request = new XMLHttpRequest();
        request.open('GET', url, true);
        request.responseType = 'arraybuffer';
        var estimated_size = (end - start) / step * VARIABLE_NUM * 4;
        var timeout = estimated_size / 10 / 1000; // ms, 10MB/s
        if (timeout < 200) {
            timeout = 200;
        }
        request.timeout = timeout;
        var response_data = await new Promise((resolve) => {
            request.onload = () => {
                if (request.status === 200) {
                    resolve(request.response);
                } else {
                    resolve(-1);
                }
            };
            request.onerror = () => {
                resolve(-1);
            };
            request.ontimeout = () => {
                resolve(-1);
            };
            request.send();
        });
        if (response_data === -1) {
            continue;
        }
        // TODO: 检查是否能用来完成当前的请求
        whole_level_caches[i] = new Uint8Array(response_data);
        if (has_request && current_request_level === i) {
            current_request_promise_resolve(1);
            has_request = false;
            current_request_promise_resolve = null;
        }
        current--;
    }
};


var cache_init = () => {
    MAX_LEVEL = Math.floor(Math.log2(TOTAL_DATA_POINTS / 40));
    if (MAX_LEVEL < 0) {
        MAX_LEVEL = 0;
    }
    MAX_CACHE_ALL_LEVEL = Math.floor(Math.log2(TOTAL_DATA_POINTS / (MAX_CACHE_ALL_SIZE / 4 / VARIABLE_NUM)));
    if (MAX_CACHE_ALL_LEVEL < 0) {
        MAX_CACHE_ALL_LEVEL = 0;
    }
    do_whole_level_cache();
};

var get_new_required_range = () => {
    var new_range = {};
    var start = current_request_start - 3 * current_window_max * Math.pow(2, current_request_level);
    var end = current_request_end + 3 * current_window_max * Math.pow(2, current_request_level);
    start = Math.round(start / Math.pow(2, current_request_level));
    end = Math.round(end / Math.pow(2, current_request_level));
    new_range[current_request_level] = {
        start: start,
        end: end
    };
    for (var i = current_request_level - 1; i >= current_request_level - 4; i--) {
        if (i < 0) {
            break;
        }
        var mouse_value = current_request_start + mouse_position * (current_request_end - current_request_start);
        var start = mouse_value - (1+mouse_position) * current_window_max * Math.pow(2, i);
        var end = mouse_value + (2-mouse_position) * current_window_max * Math.pow(2, i);
        start = Math.round(start/Math.pow(2, i));
        end = Math.round(end/Math.pow(2, i));
        new_range[i] = {
            start: start,
            end: end
        };
    }
    for (var i=current_request_level+1; i<=current_request_level+4; i++) {
        if(i>MAX_LEVEL) {
            break;
        }
        var mouse_value = current_request_start + mouse_position * (current_request_end - current_request_start);
        var start = mouse_value - (1+mouse_position) * current_window_max * Math.pow(2, i);
        var end = mouse_value + (2-mouse_position) * current_window_max * Math.pow(2, i);
        start = Math.round(start/Math.pow(2, i));
        end = Math.round(end/Math.pow(2, i));
        new_range[i] = {
            start: start,
            end: end
        };
    }
    var all_keys = Object.keys(new_range);
    for(var i=0; i<all_keys.length; i++) {
        var key = all_keys[i];
        if(whole_level_caches[key] !== undefined) {
            delete new_range[key];
        }
    }
    all_keys = Object.keys(new_range);
    for(var i=0; i<all_keys.length; i++) {
        var key = all_keys[i];
        var max_end = get_level_length(parseInt(key));
        if(new_range[key].start < 0 && new_range[key].end > max_end){
            // 为了在两端放大时, 实际缩放中心不在鼠标位置, 而是在最左边或最右边
            new_range[key].start = 0;
            new_range[key].end = max_end;
            continue;
        }
        if(new_range[key].start < 0) {
            // 为了在两端放大时, 实际缩放中心不在鼠标位置, 而是在最左边或最右边
            new_range[key].end = new_range[key].end - new_range[key].start;
            new_range[key].start = 0;
        }
        if(new_range[key].end > max_end) {
            // 为了在两端放大时, 实际缩放中心不在鼠标位置, 而是在最左边或最右边
            new_range[key].start = max_end - (new_range[key].end - new_range[key].start);
            new_range[key].end = max_end;
        }
    }
    return new_range;
};

var get_new_unnecessary_range = () => {
    var new_range = {};
    var start = current_request_start - 3 * current_window_max * Math.pow(2, current_request_level);
    var end = current_request_end + 3 * current_window_max * Math.pow(2, current_request_level);
    start = Math.round(start / Math.pow(2, current_request_level));
    end = Math.round(end / Math.pow(2, current_request_level));
    new_range[current_request_level] = {
        start: start,
        end: end
    };
    for (var i = current_request_level - 1; i >= current_request_level - 4; i--) {
        if (i < 0) {
            break;
        }
        var start = current_request_start - 2 * current_window_max * Math.pow(2, i);
        var end = current_request_end + 2 * current_window_max * Math.pow(2, i);
        start = Math.round(start/Math.pow(2, i));
        end = Math.round(end/Math.pow(2, i));
        new_range[i] = {
            start: start,
            end: end
        };
    }
    for (var i=current_request_level+1; i<=current_request_level+4; i++) {
        if(i>MAX_LEVEL) {
            break;
        }
        var start = current_request_start - 2 * current_window_max * Math.pow(2, i);
        var end = current_request_end + 2 * current_window_max * Math.pow(2, i);
        start = Math.round(start/Math.pow(2, i));
        end = Math.round(end/Math.pow(2, i));
        new_range[i] = {
            start: start,
            end: end
        };
    }
    var all_keys = Object.keys(new_range);
    for(var i=0; i<all_keys.length; i++) {
        var key = all_keys[i];
        if(whole_level_caches[key] !== undefined) {
            delete new_range[key];
        }
    }
    all_keys = Object.keys(new_range);
    for(var i=0; i<all_keys.length; i++) {
        var key = all_keys[i];
        if(new_range[key].start < 0) {
            new_range[key].start = 0;
        }
        var max_end = get_level_length(parseInt(key));
        if(new_range[key].end > max_end) {
            new_range[key].end = max_end;
        }
    }
    return new_range;
};

var update_data_range = (old_range, new_range) => {
    var old_keys = Object.keys(old_range);
    var new_keys = Object.keys(new_range);
    for(var i=0;i<old_keys.length;i++){
        if(new_range[old_keys[i]] === undefined) {
            delete old_range[old_keys[i]];
            delete cached_data[old_keys[i]];
        }
    }
    old_keys = Object.keys(old_range);
    for(var i=0;i<new_keys.length;i++){
        var key = new_keys[i];
        if(old_range[key] === undefined) {
            var length = new_range[key].end - new_range[key].start;
            var status_array = new Uint8Array(length);
            var data = new Uint8Array(length * 4 * VARIABLE_NUM);
            cached_data[key] = {
                status: status_array,
                data: data
            };
            continue;
        }
        var old_start = old_range[key].start;
        var old_end = old_range[key].end;
        var new_start = new_range[key].start;
        var new_end = new_range[key].end;
        if(new_start >= old_end || old_start >= new_end) {
            delete cached_data[key];
            var length = new_range[key].end - new_range[key].start;
            var status_array = new Uint8Array(length);
            var data = new Uint8Array(length * 4 * VARIABLE_NUM);
            cached_data[key] = {
                status: status_array,
                data: data
            };
            continue;
        }
        var shared_start = Math.max(old_start, new_start);
        var shared_end = Math.min(old_end, new_end);
        var shared_start_in_old = shared_start - old_start;
        var shared_start_in_new = shared_start - new_start;
        var shared_length = shared_end - shared_start;
        var shared_subarray_data = cached_data[key].data.subarray(shared_start_in_old * 4 * VARIABLE_NUM, (shared_start_in_old + shared_length) * 4 * VARIABLE_NUM);
        var shared_subarray_status = cached_data[key].status.subarray(shared_start_in_old, shared_start_in_old + shared_length);
        var new_data_array = new Uint8Array((new_end - new_start) * 4 * VARIABLE_NUM);
        new_data_array.set(shared_subarray_data, shared_start_in_new * 4 * VARIABLE_NUM);
        var new_status_array = new Uint8Array(new_end - new_start);
        new_status_array.set(shared_subarray_status, shared_start_in_new);
        cached_data[key] = {
            status: new_status_array,
            data: new_data_array
        };
    }
};

var create_requests = () => {
    var all_keys = Object.keys(required_cache_area);
    for (var j = 0; j < all_keys.length; j++){
        var unrequested_parts = [];
        var current_start = -1;
        var global_start = required_cache_area[all_keys[j]].start;
        var global_end = required_cache_area[all_keys[j]].end;
        var offset = unnecessary_cache_area[all_keys[j]].start;
        for(var i=global_start; i<global_end; i++){
            if(current_start === -1){
                if(cached_data[all_keys[j]].status[i -offset] === CACHE_FREE){
                    current_start = i;
                }
                continue;
            }
            if(cached_data[all_keys[j]].status[i-offset] !== CACHE_FREE){
                unrequested_parts.push([current_start, i]);
                current_start = -1;
            }
        }
        if(current_start !== -1){
            unrequested_parts.push([current_start, global_end]);
        }
        for (var i=0;i<unrequested_parts.length;i++){
            var this_start = unrequested_parts[i][0];
            var this_end = unrequested_parts[i][1];
            var this_level = parseInt(all_keys[j]);
            var step = Math.pow(2, this_level);
            var start_index = this_start;
            var end_index = this_end;
            if(this_level !== 0){
                // 如果是 0, this_start 和 this_end 就是实际的
                var start = this_start*step - step/2;
                var end = start + (this_end - this_start - 1)*step+1;
                this_start = start;
                this_end = end;
            }
            var json_data = {
                start: this_start,
                end: this_end,
                step: step,
                tr: 1 // transpose
            };
            json_data = stringToHex(JSON.stringify(json_data));
            var request_id = generate_request_id();
            ongoing_requests.add(request_id);
            var callback = create_request_callbacks(null, start_index, end_index, this_level, step, request_id);
            request_manager.add(json_data, callback, (end_index - start_index) * 4 * VARIABLE_NUM);
            cached_data[this_level].status.set(new Uint8Array(end_index - start_index).fill(CACHE_REQUESTING), start_index - offset);
        }
    }
    request_manager.flush();
};

var create_request_callbacks = (request_, start_, end_, level_, step_, request_id_) => {
    var start = start_;
    var end = end_;
    var level = level_;
    var step = step_;
    var request = request_;
    var request_id = request_id_;

    function on_load(request) {
        if(request.status !== 200){
            return;
        }
        if(ongoing_requests.has(request_id) === false){
            return;
        }
        ongoing_requests.delete(request_id);
        if(unnecessary_cache_area[level] === undefined){
            return;
        }
        var cache_start = unnecessary_cache_area[level].start;
        var cache_end = unnecessary_cache_area[level].end;
        if(start >= cache_end || end <= cache_start){
            return;
        }
        var shared_start = Math.max(start, cache_start);
        var shared_end = Math.min(end, cache_end);
        var shared_start_in_request = shared_start - start;
        var shared_start_in_cache = shared_start - cache_start;
        var shared_length = shared_end - shared_start;
        var response_data = new Uint8Array(request.response);
        cached_data[level].data.set(response_data.subarray(shared_start_in_request * 4 * VARIABLE_NUM, (shared_start_in_request + shared_length) * 4 * VARIABLE_NUM), shared_start_in_cache * 4 * VARIABLE_NUM);
        cached_data[level].status.set(new Uint8Array(shared_length).fill(CACHE_LOADED), shared_start_in_cache);
        // then need to check whether this request data can fulfill the current user request
        if(level !== current_request_level || has_request === false){
            return;
        }
        var current_start = Math.floor(current_request_start / step) + 1;
        if(level === 0){
            current_start = current_request_start;
        }
        var length = Math.floor((current_request_end - 1 - current_request_start) / step) + 1;
        var current_end = current_start + length;
        if(current_start<cache_start || current_end>cache_end){
            return;
        }
        for (var i = current_start; i < current_end; i++){
            if(cached_data[level].status[i - cache_start] !== CACHE_LOADED){
                return;
            }
        }
        current_request_promise_resolve(2);
        has_request = false;
        current_request_promise_resolve = null;
    };
    function fixed_interval_request() {
        if(ongoing_requests.has(request_id) === false){
            return;
        }
        if(required_cache_area[level] === undefined){
            return;
        }
        var cache_start = required_cache_area[level].start;
        var cache_end = required_cache_area[level].end;
        if(start >= cache_end || end <= cache_start){
            return;
        }
        var shared_start = Math.max(start, cache_start);
        var shared_end = Math.min(end, cache_end);
        var shared_start_in_cache = shared_start - cache_start;
        var shared_length = shared_end - shared_start;
        // cached_data[level].status.set(new Uint8Array(shared_length).fill(CACHE_FREE), shared_start_in_cache);
        // 对 shared_start 到 shared_end 的范围进行重试
        var retry_start = shared_start*step - step/2;
        if(level === 0){
            retry_start = shared_start;
        }
        var retry_end = retry_start + (shared_end - shared_start - 1)*step+1;
        var json_data = {
            start: retry_start,
            end: retry_end,
            step: step,
            tr: 1 // transpose
        };
        json_data = stringToHex(JSON.stringify(json_data));
        var callback = create_request_callbacks(null, shared_start, shared_end, level, step, request_id);
        request_manager.add(json_data, callback, (shared_end - shared_start) * 4 * VARIABLE_NUM);``
        // cached_data[level].status.set(new Uint8Array(shared_length).fill(CACHE_REQUESTING), shared_start_in_cache);
        // can only change the data point points where origin status is FREE, because other parts (put cache miss requested data
        // into cache) may just put data itself
        for (var i = shared_start; i < shared_end; i++){
            if(cached_data[level].status[i - cache_start] === CACHE_FREE){
                cached_data[level].status[i - cache_start] = CACHE_REQUESTING;
            }
        }
    }
    setTimeout(fixed_interval_request, 50);
    return on_load;
}

var update_cache = (mouse_move_only) => {
    // console.log('update_cache');
    if (current_request_level === -1) {
        // 这代表是图都没加载好的时候鼠标在移动, 什么都不要做
        return;
    }
    required_cache_area = get_new_required_range();
    if (mouse_move_only === false){
        var new_unnecessary_area = get_new_unnecessary_range();
        update_data_range(unnecessary_cache_area, new_unnecessary_area);
        unnecessary_cache_area = new_unnecessary_area;
    }
    create_requests();
}

var access_data_tmp = (start, end, step, window_size, window_max) => {
    var level = Math.round(Math.log2(step));
    console.log('resolved by previous cache requests');
    var length = Math.floor((end - 1 - start) / step) + 1;
    var cache_start = Math.floor(start / step) + 1; // 开始的数据在 cache 中的位置
    if (level == 0) {
        cache_start = start;
    }
    // 1. 检查 whole_level_caches 是否能满足需求
    if (level >= MAX_CACHE_ALL_LEVEL && whole_level_caches[level] !== undefined) {
        var this_level = whole_level_caches[level];
        var response_bytes = shared_bytes;
        var cache_length = this_level.length;
        var cache_point_num = cache_length / 4 / VARIABLE_NUM;
        var cache_end = cache_start + length; // actual end plus 1
        for (var i = 0; i < VARIABLE_NUM; i++) {
            var cache_start_byte = cache_point_num * 4 * i + 4 * cache_start;
            var byte_length = length * 4;
            var response_start_byte = i * length * 4;
            response_bytes.set(this_level.subarray(cache_start_byte, cache_start_byte + byte_length), response_start_byte);
        }
        has_request = false;
        return length * 4 * VARIABLE_NUM;
    }
    // 2. 检查 cached_data 是否能满足需求
    loop1: while (cached_data[level] !== undefined) {
        // 为了可以使用 break, 不用 if
        var this_start = cache_start;
        var this_end = cache_start + length;
        cache_start = unnecessary_cache_area[level].start;
        var cache_end = unnecessary_cache_area[level].end;
        if (this_start >= cache_end || this_end <= cache_start) {
            break;
        }
        for (var i = this_start; i < this_end; i++) {
            if (cached_data[level].status[i - cache_start] !== CACHE_LOADED) {
                break loop1;
            }
        }
        var result_bytes = cached_data[level].data.subarray((this_start - cache_start) * 4 * VARIABLE_NUM, (this_end - cache_start) * 4 * VARIABLE_NUM);
        shared_bytes.set(transpose_4bytes(result_bytes, VARIABLE_NUM));
        has_request = false;
        return length * 4 * VARIABLE_NUM;
    }
    throw new Error('Resolved by cache but could not find data in cache.');
};

var access_data_2 = async (start, end, step, window_size, window_max) => {
    var t1=performance.now();
    current_request_start = start;
    current_request_end = end;
    current_request_step = step;
    current_window_max = window_max;
    var level = Math.round(Math.log2(step));
    current_request_level = level;
    has_request = true;
    var length = Math.floor((end - 1 - start) / step) + 1;
    var cache_start = Math.floor(start / step) + 1; // 开始的数据在 cache 中的位置
    if (level == 0) {
        cache_start = start;
    }
    // 1. 检查 whole_level_caches 是否能满足需求
    if (level >= MAX_CACHE_ALL_LEVEL && whole_level_caches[level] !== undefined) {
        var this_level = whole_level_caches[level];
        var response_bytes = shared_bytes;
        var cache_length = this_level.length;
        var cache_point_num = cache_length / 4 / VARIABLE_NUM;
        var cache_end = cache_start + length; // actual end plus 1
        for (var i = 0; i < VARIABLE_NUM; i++) {
            var cache_start_byte = cache_point_num * 4 * i + 4 * cache_start;
            var byte_length = length * 4;
            var response_start_byte = i * length * 4;
            response_bytes.set(this_level.subarray(cache_start_byte, cache_start_byte + byte_length), response_start_byte);
        }
        has_request = false;
        // console.log(`cache hit by cache-all level, time: ${performance.now()-t1} ms`);
        return length * 4 * VARIABLE_NUM;
    }
    // 2. 检查 cached_data 是否能满足需求
    loop1: while (cached_data[level] !== undefined) {
        // 为了可以使用 break, 不用 if
        var this_start = cache_start;
        var this_end = cache_start + length;
        cache_start = unnecessary_cache_area[level].start;
        var cache_end = unnecessary_cache_area[level].end;
        if (this_start >= cache_end || this_end <= cache_start) {
            break;
        }
        for (var i = this_start; i < this_end; i++) {
            if (cached_data[level].status[i - cache_start] !== CACHE_LOADED) {
                break loop1;
            }
        }
        var result_bytes = cached_data[level].data.subarray((this_start - cache_start) * 4 * VARIABLE_NUM, (this_end - cache_start) * 4 * VARIABLE_NUM);
        shared_bytes.set(transpose_4bytes(result_bytes, VARIABLE_NUM));
        has_request = false;
        // console.log(`cache hit, time: ${performance.now()-t1} ms`);
        return length * 4 * VARIABLE_NUM;
    }
    // console.log('cache miss');
    var json_data = {
        start: start,
        end: end,
        step: step
    };
    json_data = stringToHex(JSON.stringify(json_data));
    var url = BASE_URL + '/' + json_data;
    var response_data = await new Promise((resolve) => {
        var request_id = generate_request_id();
        ongoing_requests.add(request_id);
        for (var i=0;i<3;i++){
            // 增加优先级
            create_fixed_interval_request(url, request_id, resolve);
        }
        current_request_promise_resolve = resolve;
    });
    if(response_data ===1 || response_data === 2){
        var return_value = access_data_tmp(start, end, step, window_size, window_max);
        has_request = false;
        current_request_promise_resolve = null;
        console.log(`cache miss, took ${performance.now()-t1} ms`);
        return return_value+1048576;
    }
    var response_length = response_data.byteLength;
    shared_bytes.set(new Uint8Array(response_data), 0);
    has_request = false;
    current_request_promise_resolve = null;
    // put this response data into cache
    while(cached_data[level] !== undefined){
        var this_start = Math.floor(start / step) + 1; // cache_start 前面可能修改了, 不能用
        if(level === 0){
            this_start = start;
        }
        var this_end = this_start + length;
        cache_start = unnecessary_cache_area[level].start;
        var cache_end = unnecessary_cache_area[level].end;
        if(this_start >= cache_end || this_end <= cache_start){
            break;
        }
        var new_data = transpose_4bytes(new Uint8Array(response_data), length);
        var shared_start = Math.max(this_start, cache_start);
        var shared_end = Math.min(this_end, cache_end);
        var shared_length = shared_end - shared_start;
        var shared_start_in_request = shared_start - this_start;
        var shared_start_in_cache = shared_start - cache_start;
        cached_data[level].data.set(new_data.subarray(shared_start_in_request * 4 * VARIABLE_NUM, (shared_start_in_request + shared_length) * 4 * VARIABLE_NUM), shared_start_in_cache * 4 * VARIABLE_NUM);
        cached_data[level].status.set(new Uint8Array(shared_length).fill(CACHE_LOADED), shared_start_in_cache);
        break;
    }
    console.log(`cache miss, took ${performance.now()-t1} ms`);
    return response_length+1048576;
};


var create_fixed_interval_request = (url_, request_id_, resolve_)=> {
    if(ongoing_requests.has(request_id_)===false){
        return;
    }
    var url = url_;
    var request_id = request_id_;
    var resolve = resolve_;
    var request = new XMLHttpRequest();
    request.open('GET', url, true);
    request.responseType = 'arraybuffer';
    request.onload = function () {
        if (request.status === 200) {
            if(ongoing_requests.has(request_id) === false){
                return;
            }
            ongoing_requests.delete(request_id);
            resolve(request.response);
        }
    };
    request.timeout = 500; // just to prevent last too long
    request.send();
    setTimeout(create_fixed_interval_request, 50, url, request_id, resolve);
};


var main_msg_listener = async (value) => {
    var this_value = Atomics.load(main_to_worker_signal, 0);
    var returned_value = 0;
    try {
        if (this_value === -1) {
            returned_value = -1;
        } else if (this_value === -2) {
            // TODO: change this to async, and retry when failed
            var request = new XMLHttpRequest();
            request.open('GET', BASE_URL + '/minmax', false);
            request.send();
            var response_data = base64ToArrayBuffer(request.responseText);
            var responseArray = new Uint8Array(response_data);
            shared_bytes.set(responseArray);
            returned_value = -2;
        } else if (this_value <= -3) {
            var sub_array = shared_bytes.subarray(0, -this_value);
            var sub_array_buffer = new ArrayBuffer(-this_value);
            var sub_array = new Uint8Array(sub_array_buffer);
            sub_array.set(shared_bytes.subarray(0, -this_value));
            var json_data = JSON.parse(new TextDecoder().decode(sub_array));
            var start = json_data.start;
            var end = json_data.end;
            var step = json_data.step;
            var window_size = json_data.window_size;
            var window_max = json_data.window_max;
            returned_value = await access_data_2(start, end, step, window_size, window_max);
        } else if (this_value === 1) {
            // 主线程获取统计信息, 暂定
            returned_value = 1;
            console.log("Statistics printed.");
        } else if (this_value >= 10000) {
            mouse_position = (this_value - 10000) / 10000;
            returned_value = 1;
        } else {
            throw "Unknown signal: " + this_value;
        }
    } catch (e) {
        console.log(e);
        returned_value = -5;
    }
    Atomics.store(main_to_worker_signal, 0, 0);
    Atomics.waitAsync(main_to_worker_signal, 0, 0).value.then(main_msg_listener);
    Atomics.store(worker_to_main_signal, 0, returned_value);
    if(this_value <= -3){
        update_cache(false);
    }
    if(this_value >= 10000){
        update_cache(true);
    }
}


onmessage = (e) => {
    shared_bytes = new Uint8Array(e.data.shared_bytes);
    main_to_worker_signal = new Int32Array(e.data.m2w);
    worker_to_main_signal = new Int32Array(e.data.w2m);
    BASE_URL = e.data.base_url;
    TOTAL_DATA_POINTS = e.data.total_data_points;
    VARIABLE_NUM = e.data.variable_num;
    Atomics.waitAsync(main_to_worker_signal, 0, 0).value.then(main_msg_listener);
    cache_init();
    postMessage(0);
};


// =============================== Util Functions ===============================
function base64ToArrayBuffer(base64) {
    const binaryString = atob(base64);
    const len = binaryString.length;
    const bytes = new Uint8Array(len);
    for (let i = 0; i < len; i++) {
        bytes[i] = binaryString.charCodeAt(i);
    }
    return bytes.buffer;
}

function stringToHex(str) {
    const encoder = new TextEncoder();
    const bytes = encoder.encode(str);
    let hex = '';
    for (let byte of bytes) {
        hex += byte.toString(16).padStart(2, '0');
    }
    return hex;
}

var remote_print = (msg) => {
    var request = new XMLHttpRequest();
    msg = stringToHex(msg);
    var url = '/msg/' + msg;
    var request = new XMLHttpRequest();
    request.open('GET', url, true);
    request.send();
}

var fix_up_with_remainder = (num, multiple, remainder) => {
    var tmp = num % multiple;
    if (tmp <= remainder) {
        return Math.round(num - tmp + remainder);
    }
    return Math.round(num - tmp + multiple + remainder);
};

var get_level_length = (level)=>{
    if(level === 0) {
        return TOTAL_DATA_POINTS;
    }
    var step = Math.pow(2, level);
    var start = - step / 2;
    var end = fix_up_with_remainder(TOTAL_DATA_POINTS, step, step / 2) + 1;
    var length = Math.floor((end - start -1) / step)+1;
    return length;
};

var transpose_4bytes = (array, variable_num) => {
    // create new one
    if(array.length % (4 * variable_num) !== 0) {
        throw new Error(`Array length ${array.length} is not a multiple of 4 * ${variable_num}`);
    }
    var new_array = new Uint8Array(array.length);
    var length = array.length / 4 / variable_num;
    for(var i=0;i<length;i++){
        for(var j=0;j<variable_num;j++){
            new_array.set(array.subarray(i*4*variable_num+j*4, i*4*variable_num+j*4+4), j*length*4+i*4);
        }
    }
    return new_array;
};

var generate_request_id = ()=>{
    var a = Math.floor(Math.random()*1000000000);
    var b = Math.floor(Math.random()*1000000000);
    var c = Math.floor(Math.random()*1000000000);
    return a.toString() + b.toString() + c.toString();
};

function hexToString(hexStr) {
    // Warning: ASCII only
    var str = '';
    for (var i = 0; i < hexStr.length; i += 2) {
        var hex = hexStr.substring(i, i + 2);
        str += String.fromCharCode(parseInt(hex, 16));
    }
    return str;
}
