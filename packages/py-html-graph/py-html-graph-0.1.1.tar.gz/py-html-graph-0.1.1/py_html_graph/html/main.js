console.log('py-html-graph: a high-performance interactive numpy line chart viewer, good supplement for the awful matplotlib\n\nGithub: https://github.com/jtc1246/py-html-graph');

const ACTION_IGNORE = 10000001;
const ACTION_LEFTRIGHT = 10000002;
const ACTION_UPDOWN = 10000003;


var t = 0;
const chart_element = document.getElementById('myChart');
const ctx = document.getElementById('myChart').getContext('2d');
var debug_element = document.getElementById('debug');
var debug2_element = document.getElementById('debug2');

const VARIABLE_NUM = '$jtc.py-html-graph.variable-num$'; // user-configurable
const VARIABLE_NAMES = '$jtc.py-html-graph.variable-names$'; // user-configurable
const VARIABLE_SHOW = Array.from({ length: VARIABLE_NUM }, (_, i) => true);
const LABEL_COLORS = '$jtc.py-html-graph.label-colors$'; // user-configurable

const MODE_LOAD_ONCE = 12000001;
const MODE_LOAD_AT_UPDATE = 12000002;
const MODE_PRELOAD_AND_CACHE = 12000003;

const data_loading_mode = MODE_PRELOAD_AND_CACHE;
var preload_and_cache_base_url = '$jtc.py-html-graph.data-server-base-url$'; // user-configurable
var HTTP_PORT_IN_HTTPS = '$jtc.py-html-graph.http-port-in-https$'; // open browser with --allow-running-insecure-content, open page with https, but load data with http

// 直接在 base64 里面替换, 总共就3种情况
var server_loc = '$$$jtc.py-html-graph.data-server-loc$$$'; // start with http, should not have / at the end

server_loc = server_loc.split('$').join('');

// the situation of using forwarder
if(server_loc.startsWith('http')){
    preload_and_cache_base_url = server_loc + preload_and_cache_base_url;
}

if(HTTP_PORT_IN_HTTPS.startsWith('$') === false && window.location.protocol === 'https:'){
    var tmp_url = 'http://';
    var host_str = window.location.host;
    if(host_str.indexOf(':') !== -1){
        host_str = host_str.split(':')[0];
    }
    tmp_url = tmp_url + host_str + ':' + HTTP_PORT_IN_HTTPS;
    var request = new XMLHttpRequest();
    try{
        request.open('GET', tmp_url, false);
        request.send();
        preload_and_cache_base_url = tmp_url + preload_and_cache_base_url;
        console.log("Page in HTTPS, data able to be loaded in HTTP.");
        document.getElementById('http-https').innerHTML = 'HTTP';
        document.getElementById('http-https').style.color = 'green';
    }catch(e){
        console.log("Page in HTTPS, unable to load data in HTTP, try adding --allow-running-insecure-content in browser start command.");
        document.getElementById('http-https').innerHTML = 'HTTPS';
        document.getElementById('http-https').style.color = 'red';
    }
}


if(preload_and_cache_base_url[0] === '/'){
    preload_and_cache_base_url = window.location.protocol + "//" + window.location.host + preload_and_cache_base_url;
}

var browser_info = navigator.userAgent.toLowerCase();
if((browser_info.indexOf('safari/') !== -1 && browser_info.indexOf('chrome/') === -1) || browser_info.indexOf('firefox/') !== -1){
    var main = document.getElementById('main');
    main.innerHTML = "This page can't be opened in Safari or Firefox! Please use Chrome, Edge or Opera (Recommend chrome and opera)."
    main.style.color = 'red';
    main.style.overflow = 'visible';
    main.style.fontSize = '2.5vw';
    main.style.textAlign = 'center';
    main.style.paddingTop = '10vw';
    main.style.lineHeight = '1.2';
    main.style.width = '80%';
    main.style.marginLeft = '10%';
    throw new Error();
}

if(window.location.protocol === 'http:' && !window.location.host.startsWith('127.0.0.1') && !window.location.host.startsWith('localhost')){
    var main = document.getElementById('main');
    main.innerHTML = "If using http, this page can only be opened on the same device (127.0.0.1 or localhost) as the server. Please use https or open it on the same device (through 127.0.0.1 or localhost)."
    main.innerHTML += '<p id="p1">Why?</p><p id="p2">In this webpage, I need to use sharedArrayBuffer, which requires Cross-Origin-Opener-Policy header (or the browser will not recognize sharedArrayBuffer). But if you open through http and not from 127.0.0.1 or localhost, the browser will disallow the header of Cross-Origin-Opener-Policy, so this page can\'t be opened.</p>';
    main.style.color = 'red';
    main.style.overflow = 'visible';
    main.style.fontSize = '2.5vw';
    main.style.textAlign = 'center';
    main.style.paddingTop = '5vw';
    main.style.lineHeight = '1.2';
    main.style.width = '80%';
    main.style.marginLeft = '10%';
    main.style.textAlign = 'left';
    var p1 = document.getElementById('p1');
    p1.style.fontSize = '1.5vw';
    p1.style.paddingTop = '4vw';
    p1.style.lineHeight = '1.2';
    var p2 = document.getElementById('p2');
    p2.style.fontSize = '1.5vw';
    p2.style.lineHeight = '1.25';
    p2.style.paddingTop = '1vw';
    throw new Error();
}

var cache_worker = null;
var main_to_worker_signal = null;
var worker_to_main_signal = null;
var cache_worker_shared_bytes = null;
var cache_hitting_record = [];

const cache_worker_url = 'data:application/javascript;base64,' + '$jtc.py-html-graph.inside.cacheworkerbase64$';

const totalDataPoints = '$jtc.py-html-graph.data-point-num$'; // user-configurable
const window_min = 5; // 这里不想做限制，让用户自由缩放，但是为了防止程序出现问题，设一个最小值
var window_max = 1200; // 最多可以显示的点的数量，放大时减少数量，缩小时提高level，
_ = 0                    // 除非在最小级（没有更详细的数据），实际的现实量不可以小于这个的一半,
_ = 0                    // 暂定：初始情况为最小级，但是 window 大小为 3/4
let viewWindow = 900; // 实际渲染时使用的数据点的数量
let fake_window_size = 900; // 假设在不缩放的情况下，窗口内数据点的数量
const origin_window_size = 900; // 原始窗口大小, 需要通过这个和 ratio 计算 fake_window_size
let currentIndex = 0;
/* 每次更新先更新 fake_window_size (ratio只是用于内部计算的，这里不做讨论)
   1. 如果 fake_window_size 小于 window_max (大于 window_min)，level设成0，结束, viewWindow设为 fake_window_size
   2. 如果 fake_window_size 大于 window_max, 每次除以2, level加1，直到小于等于 window_max 
      (这里对等于的情况不做过多限制, 只要小于等于window_max、大于等于它的一半就行), 最后把值赋给 viewWindow
   3. 渲染时按照 2^level 作为步长选取数据点, 共有 viewWindow 个数据点
 */
let level = 0; // 缩放级别，必须大于等于0，代表从 2^level 个数据点中选一个显示
let ratio = 1.0;
var mouseX = 0;
var mouseY = 0;
var is_touchpad = false;
var mouse_pressed = false;
var prev_mouse_loc = -1;
var reverse_mouse_direction = false;

var slider_active = false;
var precise_mouse_x = -1;
var precise_mouse_y = -1
var resizing_paddle_active = false;

window.addEventListener('mouseup', () => {
    mouse_pressed = false;
});

window.addEventListener('wheel', (event) => {
    if (event.deltaX !== 0) {
        is_touchpad = true;
    }
});

document.addEventListener('mousemove', function (event) {
    mouseX = event.clientX;
    mouseY = event.clientY;
    if (data_loading_mode !== MODE_PRELOAD_AND_CACHE) {
        return;
    }
    var mouse_x_value = getMousePosition();
    var mouse_left_ratio = (mouse_x_value - currentIndex) / fake_window_size;
    if(mouse_left_ratio<0){
        mouse_left_ratio = 0;
    }
    if(mouse_left_ratio>1){
        mouse_left_ratio = 1;
    }
    mouse_left_ratio = 10000 + Math.round(mouse_left_ratio * 10000);
    Atomics.store(main_to_worker_signal, 0, mouse_left_ratio);
    Atomics.notify(main_to_worker_signal, 0);
    while (true) {
        var signal = Atomics.load(worker_to_main_signal, 0);
        if (signal === 1) {
            break;
        }
    }
    Atomics.store(worker_to_main_signal, 0);
});

chart_element.addEventListener('wheel', function (event) {
    if(mouseX===event.clientX){
        return;
    }
    mouseX = event.clientX;
    if (data_loading_mode !== MODE_PRELOAD_AND_CACHE) {
        return;
    }
    var mouse_x_value = getMousePosition();
    var mouse_left_ratio = (mouse_x_value - currentIndex) / fake_window_size;
    if(mouse_left_ratio<0){
        mouse_left_ratio = 0;
    }
    if(mouse_left_ratio>1){
        mouse_left_ratio = 1;
    }
    mouse_left_ratio = 10000 + Math.round(mouse_left_ratio * 10000);
    Atomics.store(main_to_worker_signal, 0, mouse_left_ratio);
    Atomics.notify(main_to_worker_signal, 0);
    while (true) {
        var signal = Atomics.load(worker_to_main_signal, 0);
        if (signal === 1) {
            break;
        }
    }
    Atomics.store(worker_to_main_signal, 0);
});

if (totalDataPoints < 5) {
    document.getElementById('main').innerHTML = "Data point num can't be less than 5!";
    document.getElementById('main').style.color = 'red';
    document.getElementById('main').style.overflow = 'visible';
    document.getElementById('main').style.fontSize = '4vw';
    document.getElementById('main').style.textAlign = 'center';
    document.getElementById('main').style.paddingTop = '10vw';
    throw new Error();
}

if (totalDataPoints < viewWindow) {
    viewWindow = totalDataPoints - 1;
    fake_window_size = viewWindow;
}

var data;
var global_max = Number.MIN_VALUE;
var global_min = Number.MAX_VALUE;
var fix_y = false; // 固定为 global 的范围
var fit_y_current = false; // 每次之前设为 true, 结束之后就设为 false
var lock_y = false; // 这个为 true 的情况下, fix_y 应设成 false, 并把另两个按钮锁定
var current_max = Number.MIN_VALUE;
var current_min = Number.MAX_VALUE;
var prev_y_max = null;
var prev_y_min = null;
var graph_locked = false;
var latest_line_width = 0;
var previous_window_width = document.querySelector('main').clientWidth;

const numWorkers = VARIABLE_NUM;
const workers = [];
const dataSets = new Array(VARIABLE_NUM).fill(null);
let completedWorkers = 0;
var all_finished = false;
var generating_start_time = performance.now();

var create_label_callback = (index) => {
    var tmp = index;
    var callback = () => {
        var element = document.getElementById(`label-checkbox-${tmp}`);
        if (element.checked) {
            VARIABLE_SHOW[tmp] = true;
        } else {
            const trueCount = VARIABLE_SHOW.filter(value => value).length;
            VARIABLE_SHOW[tmp] = false;
        }
        myChart.destroy();
        myChart = createChart_for_show_hide_variable();
    };
    return callback;
};

var select_all_variables = () => {
    for (var i = 0; i < VARIABLE_NUM; i++) {
        VARIABLE_SHOW[i] = true;
        document.getElementById(`label-checkbox-${i}`).checked = true;
    }
    myChart.destroy();
    myChart = createChart_for_show_hide_variable();
}

var unselect_all_variables = () => {
    for (var i = 0; i < VARIABLE_NUM; i++) {
        VARIABLE_SHOW[i] = false;
        document.getElementById(`label-checkbox-${i}`).checked = false;
    }
    myChart.destroy();
    myChart = createChart_for_show_hide_variable();
}

var set_labels = () => {
    var label_container = document.getElementById('labels');
    var max_width = 0;
    var graph_height = chart_element.clientHeight;
    var window_width_2 = document.querySelector('main').clientWidth;
    var graph_height_vw = graph_height / window_width_2 * 100;
    var per_label_height = graph_height_vw / (VARIABLE_NUM+1);
    if (per_label_height > 2) {
        per_label_height = 2;
    }
    if (per_label_height < 1.34) {
        per_label_height = 1.34;
    }
    document.getElementById('sel-uns-all').style.height = per_label_height + 'vw';
    for (var i = 0; i < VARIABLE_NUM; i++) {
        var this_label = document.createElement('div');
        this_label.classList.add('label');
        this_label.style.height = per_label_height + 'vw';
        var label_input = document.createElement('input');
        label_input.type = 'checkbox';
        label_input.checked = 'true';
        label_input.id = `label-checkbox-${i}`;
        label_input.addEventListener('change', create_label_callback(i));
        this_label.appendChild(label_input);
        var color_line = document.createElement('div');
        color_line.classList.add('line-color');
        color_line.style.backgroundColor = LABEL_COLORS[i];
        this_label.appendChild(color_line);
        var label_text = document.createElement('p');
        label_text.innerHTML = VARIABLE_NAMES[i];
        this_label.appendChild(label_text);
        label_container.appendChild(this_label);
        var this_width = label_text.getBoundingClientRect().width;
        if (this_width > max_width) {
            max_width = this_width;
        }
    }
    var window_width = document.querySelector('main').clientWidth;
    var max_width_in_vw = max_width / window_width * 100;
    max_width_in_vw += 5;
    document.getElementById('wrapper').style.setProperty('--labels-width-vw', max_width_in_vw);
};

set_labels();
document.querySelector('body').style.display = 'none';

function createData() {
    if (data_loading_mode === MODE_LOAD_ONCE) {
        return new Promise((resolve) => {
            var request = new XMLHttpRequest();
            request.open('GET', load_once_url, true);
            request.timeout = 200000;
            request.responseType = 'arraybuffer';
            request.onerror = () => {
                console.log(' Request Error');
            };
            request.ontimeout = () => {
                console.log('Request Timeout');
            };
            request.onload = () => {
                var data = request.response;
                console.log(data.byteLength);
                if (data.byteLength !== VARIABLE_NUM * 4 * totalDataPoints) {
                    console.log('Data Error');
                    return;
                }
                var view = new DataView(data);
                for (var i = 0; i < VARIABLE_NUM; i++) {
                    var list = []
                    for (var j = 0; j < totalDataPoints; j++) {
                        var number = view.getFloat32(i * 4 * totalDataPoints + j * 4, false);
                        list.push(number);
                    }
                    dataSets[i] = list;
                }
                resolve(dataSets);
            };
            request.send();
        });
    }
    if (data_loading_mode === MODE_LOAD_AT_UPDATE) {
        return new Promise((resolve) => {
            var request = new XMLHttpRequest();
            request.open('GET', load_at_update_base_url + '/minmax', true);
            request.onload = () => {
                var b64data = request.responseText;
                var data = base64ToArrayBuffer(b64data);
                var view = new DataView(data);
                global_min = view.getFloat32(0, false);
                global_max = view.getFloat32(4, false);
                resolve(null);
            };
            request.send();
        });
    }
    if (data_loading_mode === MODE_PRELOAD_AND_CACHE) {
        return new Promise((resolve) => {
            cache_worker = new Worker(cache_worker_url);
            var mtow_array = new SharedArrayBuffer(4);
            main_to_worker_signal = new Int32Array(mtow_array);
            var wtom_array = new SharedArrayBuffer(4);
            worker_to_main_signal = new Int32Array(wtom_array);
            var shared_bytes = new SharedArrayBuffer(1000000);
            cache_worker_shared_bytes = new Uint8Array(shared_bytes);
            Atomics.store(main_to_worker_signal, 0, 0);
            Atomics.store(worker_to_main_signal, 0, 0);
            cache_worker.postMessage({
                first: true,
                m2w: mtow_array,
                w2m: wtom_array,
                shared_bytes: shared_bytes,
                base_url: preload_and_cache_base_url,
                total_data_points: totalDataPoints,
                variable_num: VARIABLE_NUM
            });
            cache_worker.onmessage = (e) => {
                resolve(null);
            };
        });
    }
}

var find_global_min_max = (data) => {
    for (var i = 0; i < data.length; i++) {
        var current = data[i].data;
        var l = current.length;
        for (var j = 0; j < l; j++) {
            if (current[j] > global_max) {
                global_max = current[j];
            }
            if (current[j] < global_min) {
                global_min = current[j];
            }
        }
    }
};

var update_range = () => {
    /* 如果在之前的范围内, 且差小于之前差的 40%, 就不更新
       每次更新, 把 max 上调 1/3, min 下调 1/3
       如果 max大于global_max 或 min小于global_min, 就使用 global_max 或 global_min
     */
    if (lock_y) {
        return;
    }
    if (fit_y_current) {
        diff = current_max - current_min;
        prev_y_max = current_max + diff * 0.02;
        prev_y_min = current_min - diff * 0.02;
        return;
    }
    if (prev_y_max === null || prev_y_min === null) {
        var diff = current_max - current_min;
        prev_y_max = current_max + diff / 3;
        prev_y_min = current_min - diff / 3;
        if (prev_y_max > global_max) {
            prev_y_max = global_max;
        }
        if (prev_y_min < global_min) {
            prev_y_min = global_min;
        }
        return;
    }
    if (current_min >= prev_y_min && current_max <= prev_y_max && (current_max - current_min) >= 0.4 * (prev_y_max - prev_y_min)) {
        return;
    }
    var diff = current_max - current_min;
    prev_y_max = current_max + diff / 3;
    prev_y_min = current_min - diff / 3;
    if (prev_y_max > global_max) {
        prev_y_max = global_max;
    }
    if (prev_y_min < global_min) {
        prev_y_min = global_min;
    }
};

var get_y_min = () => {
    if (fix_y) {
        return global_min;
    }
    update_range();
    return prev_y_min;
}

var get_y_max = () => {
    if (fix_y) {
        return global_max;
    }
    return prev_y_max;
}

var mouse_drag = (event) => {
    if (is_touchpad || !mouse_pressed) {
        return;
    }
    var tmp = event.clientX;
    var moved = tmp - prev_mouse_loc;
    if (moved === 0) {
        return;
    }
    event.preventDefault();
    prev_mouse_loc = tmp;
    handle_x_drag(-moved);
};

var window_resize = () => {
    var new_window_width = document.querySelector('main').clientWidth;
    var new_width = latest_line_width / previous_window_width * document.querySelector('main').clientWidth;
    previous_window_width = new_window_width;
    update_line_width_only(new_width);
};

createData().then((dataSets) => {
    if (data_loading_mode === MODE_LOAD_ONCE) {
        data = {
            datasets: dataSets.map((data, i) => ({
                data: data
            }))
        };
        find_global_min_max(data.datasets);
    }
    if (data_loading_mode === MODE_PRELOAD_AND_CACHE) {
        // console.log('Worker ready');
        Atomics.store(main_to_worker_signal, 0, -1);
        Atomics.notify(main_to_worker_signal, 0);
        while (true) {
            var signal = Atomics.load(worker_to_main_signal, 0);
            if (signal === -1) {
                // console.log('Worker responded');
                break;
            }
        }
        Atomics.store(worker_to_main_signal, 0, 0);
        Atomics.store(main_to_worker_signal, 0, -2);
        Atomics.notify(main_to_worker_signal, 0);
        while (true) {
            var signal = Atomics.load(worker_to_main_signal, 0);
            if (signal === -2) {
                // console.log('Min max value got');
                break;
            }
        }
        var view = new DataView(cache_worker_shared_bytes.buffer, 0, 8);
        var min = view.getFloat32(0, false);
        var max = view.getFloat32(4, false);
        global_max = max;
        global_min = min;
        // console.log(`Global max: ${global_max}, Global min: ${global_min}`);
    }
    all_finished = true;
    // console.log(`Time to generate data: ${performance.now() - generating_start_time} ms`);
    document.querySelector('body').style.display = 'block';
    updateChart();
    element.addEventListener('wheel', handle_wheel, { passive: false });
    window.addEventListener('resize', window_resize);
    title_element.style.lineHeight = title_element.clientHeight + "px";
    previous_window_width = document.querySelector('main').clientWidth;
    element.addEventListener('mousedown', (event) => {
        mouse_pressed = true;
        prev_mouse_loc = event.clientX;
    });
    element.addEventListener('mousemove', mouse_drag);
});

let myChart;
var fps_datas = [];
var last_update_time = 0;

function slice_no_min_max(arr, start, end_plus_one, step) {
    var result = [];
    var origin_end_plus_one = end_plus_one;
    if (end_plus_one > arr.length) {
        end_plus_one = arr.length;
    }
    if (start >= 0) {
        result.push(arr[start]);
    } else {
        result.push(arr[0]);
    }
    for (var i = start + step; i < end_plus_one; i += step) {
        result.push(arr[i]);
    }
    var ideal_length = Math.floor((origin_end_plus_one - 1 - start) / step) + 1;
    if (result.length < ideal_length) {
        result.push(arr[arr.length - 1]);
    }
    return result;
}

function slice(arr, start, end_plus_one, step) {
    var result = [];
    var origin_end_plus_one = end_plus_one;
    if (end_plus_one > arr.length) {
        end_plus_one = arr.length;
    }
    if (start >= 0) {
        result.push(arr[start]);
        if (arr[start] > current_max) {
            current_max = arr[start];
        }
        if (arr[start] < current_min) {
            current_min = arr[start];
        }
    } else {
        result.push(arr[0]);
        if (arr[0] > current_max) {
            current_max = arr[0];
        }
        if (arr[0] < current_min) {
            current_min = arr[0];
        }
    }
    for (var i = start + step; i < end_plus_one; i += step) {
        result.push(arr[i]);
        if (arr[i] > current_max) {
            current_max = arr[i];
        }
        if (arr[i] < current_min) {
            current_min = arr[i];
        }
    }
    var ideal_length = Math.floor((origin_end_plus_one - 1 - start) / step) + 1;
    if (result.length < ideal_length) {
        result.push(arr[arr.length - 1]);
        if (arr[arr.length - 1] > current_max) {
            current_max = arr[arr.length - 1];
        }
        if (arr[arr.length - 1] < current_min) {
            current_min = arr[arr.length - 1];
        }
    }
    return result;
}

var fix_down_with_remainder = (num, multiple, remainder) => {
    var tmp = num % multiple;
    if (tmp >= remainder) {
        return Math.round(num - tmp + remainder);
    }
    return Math.round(num - tmp - multiple + remainder);
};

var fix_up_with_remainder = (num, multiple, remainder) => {
    var tmp = num % multiple;
    if (tmp <= remainder) {
        return Math.round(num - tmp + remainder);
    }
    return Math.round(num - tmp + multiple + remainder);
};

var prev_config = null;

function create_chartjs_x_values(start, end_plus_one, step) {
    var result = [];
    var origin_end_plus_one = end_plus_one;
    if (end_plus_one > totalDataPoints) {
        end_plus_one = totalDataPoints;
    }
    if (start >= 0) {
        result.push(start);
    } else {
        result.push(0);
    }
    for (var i = start + step; i < end_plus_one; i += step) {
        result.push(i);
    }
    var ideal_length = Math.floor((origin_end_plus_one - 1 - start) / step) + 1;
    if (result.length < ideal_length) {
        result.push(totalDataPoints - 1);
    }
    return result;
}

function base64ToArrayBuffer(base64) {
    const binaryString = atob(base64);
    const len = binaryString.length;
    const bytes = new Uint8Array(len);
    for (let i = 0; i < len; i++) {
        bytes[i] = binaryString.charCodeAt(i);
    }
    return bytes.buffer;
}

function createChart() {
    debug2_element.innerHTML = `currentIndex: ${currentIndex.toFixed(6)}<br>fake_window_size: ${fake_window_size.toFixed(6)}<br>viewWindow: ${viewWindow.toFixed(6)}<br>level: ${level}<br>ratio: ${ratio.toFixed(6)}`;
    var step = Math.pow(2, level);
    var remainder = 0;
    if (level !== 0) {
        remainder = Math.pow(2, level - 1);
    }
    var start = fix_down_with_remainder(currentIndex, step, remainder);
    var end_plus_one = fix_up_with_remainder(currentIndex + fake_window_size, step, remainder) + 1;
    current_min = Number.MAX_VALUE;
    current_max = Number.MIN_VALUE;
    if (latest_line_width === 0) {
        latest_line_width = document.querySelector('main').clientWidth / 300 * 28 / 100;
    }
    var config;
    if (data_loading_mode === MODE_LOAD_ONCE) {
        config = {
            type: 'line',
            data: {
                labels: create_chartjs_x_values(start, end_plus_one, step),
                datasets: data.datasets.filter((_, i) => VARIABLE_SHOW[i]).map(dataset => ({
                    ...dataset,
                    data: slice(dataset.data, start, end_plus_one, step),
                    borderColor: LABEL_COLORS[data.datasets.indexOf(dataset)],
                    pointRadius: 0,
                    borderWidth: latest_line_width,
                    tension: 0,
                    borderJoinStyle: 'round'
                }))
            },
            options: {
                animation: false,
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        enabled: false
                    }
                },
                scales: {
                    x: {
                        type: 'linear',
                        min: (currentIndex),
                        max: (currentIndex + fake_window_size),
                        display: false
                    },
                    y: {
                        display: false,
                        min: get_y_min(),
                        max: get_y_max()
                    }
                },
                interaction: {
                    mode: null
                }
            }
        };
    }
    if (data_loading_mode === MODE_LOAD_AT_UPDATE) {
        var json_data = {
            start: start,
            end: end_plus_one,
            step: step
        }
        json_data = stringToHex(JSON.stringify(json_data));
        url = load_at_update_base_url + '/' + json_data;
        var request = new XMLHttpRequest();
        request.open('GET', url, false);
        var send_time = performance.now();
        request.send();
        console.log(`Time to get data: ${performance.now() - send_time} ms`);
        var response_data = request.responseText;
        response_data = base64ToArrayBuffer(response_data);
        var view = new DataView(response_data);
        var datasets = [];
        var length = response_data.byteLength / VARIABLE_NUM / 4;
        for (var i = 0; i < VARIABLE_NUM; i++) {
            var list = [];
            for (var j = 0; j < length; j++) {
                var number = view.getFloat32(i * 4 * length + j * 4, false);
                list.push(number);
                if (number > current_max && VARIABLE_SHOW[i]) {
                    current_max = number;
                }
                if (number < current_min && VARIABLE_SHOW[i]) {
                    current_min = number;
                }
            }
            datasets.push(list);
        }
        config = {
            type: 'line',
            data: {
                labels: create_chartjs_x_values(start, end_plus_one, step),
                datasets: datasets.filter((_, i) => VARIABLE_SHOW[i]).map(dataset => ({
                    data: dataset,
                    borderColor: LABEL_COLORS[datasets.indexOf(dataset)],
                    pointRadius: 0,
                    borderWidth: latest_line_width,
                    tension: 0,
                    borderJoinStyle: 'round'
                }))
            },
            options: {
                animation: false,
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        enabled: false
                    }
                },
                scales: {
                    x: {
                        type: 'linear',
                        min: (currentIndex),
                        max: (currentIndex + fake_window_size),
                        display: false
                    },
                    y: {
                        display: false,
                        min: get_y_min(),
                        max: get_y_max()
                    }
                },
                interaction: {
                    mode: null
                }
            }
        };
    }
    if (data_loading_mode === MODE_PRELOAD_AND_CACHE) {
        var json_data = {
            start: start,
            end: end_plus_one,
            step: step,
            window_size: viewWindow,
            window_max: window_max
        }
        json_data = JSON.stringify(json_data);
        var string_length = json_data.length;
        cache_worker_shared_bytes.set(new TextEncoder().encode(json_data), 0);
        Atomics.store(main_to_worker_signal, 0, -string_length);
        Atomics.notify(main_to_worker_signal, 0);
        var result_length;
        while (true) {
            var signal = Atomics.load(worker_to_main_signal, 0);
            if (signal >= 1) {
                result_length = signal;
                break;
            }
        }
        if(result_length >= 1048576){
            cache_hitting_record.push(false);
            result_length -= 1048576;
        } else {
            cache_hitting_record.push(true);
        }
        update_cache_hitting_ratio();
        Atomics.store(worker_to_main_signal, 0, 0);
        var response_data = cache_worker_shared_bytes.buffer.slice(0, result_length);
        var view = new DataView(response_data);
        var datasets = [];
        var length = response_data.byteLength / VARIABLE_NUM / 4;
        for (var i = 0; i < VARIABLE_NUM; i++) {
            var list = [];
            for (var j = 0; j < length; j++) {
                var number = view.getFloat32(i * 4 * length + j * 4, false);
                list.push(number);
                if (number > current_max && VARIABLE_SHOW[i]) {
                    current_max = number;
                }
                if (number < current_min && VARIABLE_SHOW[i]) {
                    current_min = number;
                }
            }
            datasets.push(list);
        }
        config = {
            type: 'line',
            data: {
                labels: create_chartjs_x_values(start, end_plus_one, step),
                datasets: datasets.filter((_, i) => VARIABLE_SHOW[i]).map(dataset => ({
                    data: dataset,
                    borderColor: LABEL_COLORS[datasets.indexOf(dataset)],
                    pointRadius: 0,
                    borderWidth: latest_line_width,
                    tension: 0,
                    borderJoinStyle: 'round'
                }))
            },
            options: {
                animation: false,
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        enabled: false
                    }
                },
                scales: {
                    x: {
                        type: 'linear',
                        min: (currentIndex),
                        max: (currentIndex + fake_window_size),
                        display: false
                    },
                    y: {
                        display: false,
                        min: get_y_min(),
                        max: get_y_max()
                    }
                },
                interaction: {
                    mode: null
                }
            }
        };
    }
    prev_config = config;
    fit_y_current = false;
    var chart_y_min = config.options.scales.y.min;
    var chart_y_max = config.options.scales.y.max;
    set_y_value(chart_y_min, chart_y_max);
    set_x_value();
    return new Chart(ctx, config);
}

var update_cache_hitting_ratio = () => {
    if(cache_hitting_record.length>=2000){
        cache_hitting_record.shift();
    }
    const true_count = cache_hitting_record.filter(value => value).length;
    var ratio = (100 * (true_count / cache_hitting_record.length)).toFixed(2);
    var cache_rate = document.getElementById('cache-rate');
    cache_rate.innerHTML = 'Cache hit: ' + ratio + '%';
};

function createChart_for_show_hide_variable() {
    debug2_element.innerHTML = `currentIndex: ${currentIndex.toFixed(6)}<br>fake_window_size: ${fake_window_size.toFixed(6)}<br>viewWindow: ${viewWindow.toFixed(6)}<br>level: ${level}<br>ratio: ${ratio.toFixed(6)}`;
    var step = Math.pow(2, level);
    var remainder = 0;
    if (level !== 0) {
        remainder = Math.pow(2, level - 1);
    }
    var start = fix_down_with_remainder(currentIndex, step, remainder);
    var end_plus_one = fix_up_with_remainder(currentIndex + fake_window_size, step, remainder) + 1;
    current_min = Number.MAX_VALUE;
    current_max = Number.MIN_VALUE;
    if (latest_line_width === 0) {
        latest_line_width = document.querySelector('main').clientWidth / 300 * 28 / 100;
    }
    var config;
    if (data_loading_mode === MODE_LOAD_ONCE) {
        config = {
            type: 'line',
            data: {
                labels: create_chartjs_x_values(start, end_plus_one, step),
                datasets: data.datasets.filter((_, i) => VARIABLE_SHOW[i]).map(dataset => ({
                    ...dataset,
                    data: slice_no_min_max(dataset.data, start, end_plus_one, step),
                    borderColor: LABEL_COLORS[data.datasets.indexOf(dataset)],
                    pointRadius: 0,
                    borderWidth: latest_line_width,
                    tension: 0,
                    borderJoinStyle: 'round'
                }))
            },
            options: {
                animation: false,
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        enabled: false
                    }
                },
                scales: {
                    x: {
                        type: 'linear',
                        min: (currentIndex),
                        max: (currentIndex + fake_window_size),
                        display: false
                    },
                    y: {
                        display: false,
                        min: prev_config.options.scales.y.min,
                        max: prev_config.options.scales.y.max
                    }
                },
                interaction: {
                    mode: null
                }
            }
        };
    }
    if (data_loading_mode === MODE_LOAD_AT_UPDATE) {
        var json_data = {
            start: start,
            end: end_plus_one,
            step: step
        }
        json_data = stringToHex(JSON.stringify(json_data));
        url = load_at_update_base_url + '/' + json_data;
        var request = new XMLHttpRequest();
        request.open('GET', url, false);
        request.send();
        var response_data = request.responseText;
        response_data = base64ToArrayBuffer(response_data);
        var view = new DataView(response_data);
        var datasets = [];
        var length = response_data.byteLength / VARIABLE_NUM / 4;
        for (var i = 0; i < VARIABLE_NUM; i++) {
            var list = [];
            for (var j = 0; j < length; j++) {
                var number = view.getFloat32(i * 4 * length + j * 4, false);
                list.push(number);
            }
            datasets.push(list);
        }
        config = {
            type: 'line',
            data: {
                labels: create_chartjs_x_values(start, end_plus_one, step),
                datasets: datasets.filter((_, i) => VARIABLE_SHOW[i]).map(dataset => ({
                    data: dataset,
                    borderColor: LABEL_COLORS[datasets.indexOf(dataset)],
                    pointRadius: 0,
                    borderWidth: latest_line_width,
                    tension: 0,
                    borderJoinStyle: 'round'
                }))
            },
            options: {
                animation: false,
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        enabled: false
                    }
                },
                scales: {
                    x: {
                        type: 'linear',
                        min: (currentIndex),
                        max: (currentIndex + fake_window_size),
                        display: false
                    },
                    y: {
                        display: false,
                        min: prev_config.options.scales.y.min,
                        max: prev_config.options.scales.y.max
                    }
                },
                interaction: {
                    mode: null
                }
            }
        };
    }
    if (data_loading_mode === MODE_PRELOAD_AND_CACHE) {
        var json_data = {
            start: start,
            end: end_plus_one,
            step: step,
            window_size: viewWindow,
            window_max: window_max
        }
        json_data = JSON.stringify(json_data);
        var string_length = json_data.length;
        cache_worker_shared_bytes.set(new TextEncoder().encode(json_data), 0);
        Atomics.store(main_to_worker_signal, 0, -string_length);
        Atomics.notify(main_to_worker_signal, 0);
        var result_length;
        while (true) {
            var signal = Atomics.load(worker_to_main_signal, 0);
            if (signal >= 1) {
                result_length = signal;
                break;
            }
        }
        if(result_length >= 1048576){
            cache_hitting_record.push(false);
            result_length -= 1048576;
        } else {
            cache_hitting_record.push(true);
        }
        update_cache_hitting_ratio();
        Atomics.store(worker_to_main_signal, 0, 0);
        var response_data = cache_worker_shared_bytes.buffer.slice(0, result_length);
        var view = new DataView(response_data);
        var datasets = [];
        var length = response_data.byteLength / VARIABLE_NUM / 4;
        for (var i = 0; i < VARIABLE_NUM; i++) {
            var list = [];
            for (var j = 0; j < length; j++) {
                var number = view.getFloat32(i * 4 * length + j * 4, false);
                list.push(number);
            }
            datasets.push(list);
        }
        config = {
            type: 'line',
            data: {
                labels: create_chartjs_x_values(start, end_plus_one, step),
                datasets: datasets.filter((_, i) => VARIABLE_SHOW[i]).map(dataset => ({
                    data: dataset,
                    borderColor: LABEL_COLORS[datasets.indexOf(dataset)],
                    pointRadius: 0,
                    borderWidth: latest_line_width,
                    tension: 0,
                    borderJoinStyle: 'round'
                }))
            },
            options: {
                animation: false,
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        enabled: false
                    }
                },
                scales: {
                    x: {
                        type: 'linear',
                        min: (currentIndex),
                        max: (currentIndex + fake_window_size),
                        display: false
                    },
                    y: {
                        display: false,
                        min: prev_config.options.scales.y.min,
                        max: prev_config.options.scales.y.max
                    }
                },
                interaction: {
                    mode: null
                }
            }
        };
    }
    prev_config = config;
    fit_y_current = false;
    var chart_y_min = config.options.scales.y.min;
    var chart_y_max = config.options.scales.y.max;
    set_y_value(chart_y_min, chart_y_max);
    set_x_value();
    return new Chart(ctx, config);
}

var update_line_width_only = (new_width) => {
    latest_line_width = new_width;
    prev_config.data.datasets.forEach((dataset) => {
        dataset.borderWidth = new_width;
    });
    myChart.destroy();
    myChart = new Chart(ctx, prev_config);
    var time = performance.now() - t;
    if (time > 500) {
        t = performance.now();
        return;
    }
    fps_datas.push(time);
    if (fps_datas.length > 10) {
        fps_datas.shift();
    }
    if (performance.now() - last_update_time > 150) {
        last_update_time = performance.now();
        var sum = 0;
        for (var i = 0; i < fps_datas.length; i++) {
            sum += fps_datas[i];
        }
        time = sum / fps_datas.length;
        var fps = 1000 / time;
        var e = document.getElementById("fps");
        e.innerHTML = `FPS: ${fps.toFixed(2)}`;
    }
    t = performance.now();
};


// Function to update the chart view window by recreating the chart
function updateChart() {
    if (myChart) {
        myChart.destroy();
    }
    myChart = createChart();
    var time = performance.now() - t;
    if (time > 500) {
        t = performance.now();
        return;
    }
    fps_datas.push(time);
    if (fps_datas.length > 10) {
        fps_datas.shift();
    }
    if (performance.now() - last_update_time > 150) {
        last_update_time = performance.now();
        var sum = 0;
        for (var i = 0; i < fps_datas.length; i++) {
            sum += fps_datas[i];
        }
        time = sum / fps_datas.length;
        var fps = 1000 / time;
        var e = document.getElementById("fps");
        e.innerHTML = `FPS: ${fps.toFixed(2)}`;
    }
    t = performance.now();
}


function handle_wheel(event) {
    if (event.deltaX !== 0) {
        is_touchpad = true;
    }
    event.preventDefault();
    if (graph_locked) {
        return;
    }
    var y = event.deltaY;
    var x = event.deltaX;
    // Currently will not implement this (distinguish whether it is mouse or touchpad, reverse
    // the direction if it is mouse), the following method works on mac, but not works on linux.
    // var tmptmp = Math.abs(y) % 1;
    // if(tmptmp >0.0001 && tmptmp < 0.9999) {
    //     y = -y;
    // }
    if (reverse_mouse_direction) {
        y = -y;
    }
    var action = -1;
    if (y === 0) {
        action = ACTION_LEFTRIGHT;
    } else if (x === 0) {
        action = ACTION_UPDOWN;
    } else if (Math.abs(y) >= 2 * Math.abs(x)) {
        action = ACTION_UPDOWN;
    } else if (Math.abs(x) >= 2 * Math.abs(y)) {
        action = ACTION_LEFTRIGHT;
    } else {
        action = ACTION_IGNORE;
    }
    if (action === ACTION_IGNORE) {
        return;
    }
    if (action === ACTION_LEFTRIGHT) {
        currentIndex += x * fake_window_size / 1000;
        if (currentIndex < 0) {
            currentIndex = 0;
        }
        if (currentIndex > totalDataPoints - fake_window_size - 1) {
            currentIndex = totalDataPoints - fake_window_size - 1;
        }
    }
    if (action === ACTION_UPDOWN) {
        // 防止缩放过快来不及缓存
        if(Math.pow(1.0025, y)>1.5){
            ratio *=1.5
        }else if(Math.pow(1.0025, y)<2/3){
            ratio *=2/3
        }else{
        ratio *= Math.pow(1.0025, y);
        }
        var prev_fake_window_size = fake_window_size;
        fake_window_size = origin_window_size * ratio;
        if (fake_window_size < window_min) {
            fake_window_size = window_min;
            ratio = fake_window_size / origin_window_size;
        }
        if (fake_window_size > totalDataPoints - 1) {
            fake_window_size = totalDataPoints - 1;
            ratio = fake_window_size / origin_window_size;
        }
        var mouse_x = getMousePosition();
        var left_ratio = (mouse_x - currentIndex) / prev_fake_window_size;
        currentIndex = mouse_x - fake_window_size * left_ratio;
        if (currentIndex < 0) {
            currentIndex = 0;
        }
        if (currentIndex > totalDataPoints - fake_window_size - 1) {
            currentIndex = totalDataPoints - fake_window_size - 1;
        }
        // 开始处理 level 和 viewWindow, 因为实际上前面只是计算范围, 
        // 和实际渲染完全没关系, currentIndex 可以先计算好
        level = 0;
        viewWindow = fake_window_size;
        while (viewWindow > window_max) {
            viewWindow /= 2;
            level++;
        }
    }
    debug_element.innerHTML = `currentIndex: ${currentIndex.toFixed(6)}<br>fake_window_size: ${fake_window_size.toFixed(6)}<br>viewWindow: ${viewWindow.toFixed(6)}<br>level: ${level}<br>ratio: ${ratio.toFixed(6)}`;
    updateChart();
}

function handle_x_drag(moved_x) {
    if (graph_locked) {
        return;
    }
    var y = 0;
    var x = moved_x;
    var action = -1;
    if (y === 0) {
        action = ACTION_LEFTRIGHT;
    } else if (x === 0) {
        action = ACTION_UPDOWN;
    } else if (Math.abs(y) >= 3 * Math.abs(x)) {
        action = ACTION_UPDOWN;
    } else if (Math.abs(x) >= 3 * Math.abs(y)) {
        action = ACTION_LEFTRIGHT;
    } else {
        action = ACTION_IGNORE;
    }
    if (action === ACTION_IGNORE) {
        return;
    }
    if (action === ACTION_LEFTRIGHT) {
        currentIndex += x * fake_window_size / chart_element.clientWidth;
        if (currentIndex < 0) {
            currentIndex = 0;
        }
        if (currentIndex > totalDataPoints - fake_window_size - 1) {
            currentIndex = totalDataPoints - fake_window_size - 1;
        }
    }
    if (action === ACTION_UPDOWN) {
        // 防止缩放过快来不及缓存
        if(Math.pow(1.0025, y)>1.5){
            ratio *=1.5
        }else if(Math.pow(1.0025, y)<2/3){
            ratio *=2/3
        }else{
        ratio *= Math.pow(1.0025, y);
        }
        var prev_fake_window_size = fake_window_size;
        fake_window_size = origin_window_size * ratio;
        if (fake_window_size < window_min) {
            fake_window_size = window_min;
            ratio = fake_window_size / origin_window_size;
        }
        if (fake_window_size > totalDataPoints - 1) {
            fake_window_size = totalDataPoints - 1;
            ratio = fake_window_size / origin_window_size;
        }
        var mouse_x = getMousePosition();
        var left_ratio = (mouse_x - currentIndex) / prev_fake_window_size;
        currentIndex = mouse_x - fake_window_size * left_ratio;
        if (currentIndex < 0) {
            currentIndex = 0;
        }
        if (currentIndex > totalDataPoints - fake_window_size - 1) {
            currentIndex = totalDataPoints - fake_window_size - 1;
        }
        // 开始处理 level 和 viewWindow, 因为实际上前面只是计算范围, 
        // 和实际渲染完全没关系, currentIndex 可以先计算好
        level = 0;
        viewWindow = fake_window_size;
        while (viewWindow > window_max) {
            viewWindow /= 2;
            level++;
        }
    }
    debug_element.innerHTML = `currentIndex: ${currentIndex.toFixed(6)}<br>fake_window_size: ${fake_window_size.toFixed(6)}<br>viewWindow: ${viewWindow.toFixed(6)}<br>level: ${level}<br>ratio: ${ratio.toFixed(6)}`;
    updateChart();
}

var element = document.getElementById('myChart');

function getMousePosition() {
    const canvas = document.getElementById('myChart');
    const rect = canvas.getBoundingClientRect();
    const mouse_X = mouseX - rect.left;
    const xValue = myChart.scales.x.getValueForPixel(mouse_X);
    return xValue;
}

var fix_y_checkbox = document.getElementById('fix-y');
var fix_y_wrapper = document.getElementById('fix-y-wrapper');
var fix_y_mask_element = document.getElementById('fix-y-mask');
fix_y_checkbox.addEventListener('change', () => {
    if (lock_y) {
        if (fix_y_checkbox.checked) {
            fix_y_checkbox.checked = false;
        }
        return;
    }
    if (fix_y_checkbox.checked) {
        fit_y_element.classList.add('invalid');
        fix_y = true;
    } else {
        fit_y_element.classList.remove('invalid');
        fix_y = false;
    }
    updateChart();
});

var fit_y_element = document.getElementById('to-current');
var fit_current = () => {
    if (lock_y || fix_y) {
        return;
    }
    fit_y_current = true;
    updateChart();
};

var set_y_low = document.getElementById('y-range-1');
var set_y_high = document.getElementById('y-range-2');
var set_y_range = () => {
    var low = parseFloat(set_y_low.value);
    var high = parseFloat(set_y_high.value);
    if (Number.isNaN(low) || Number.isNaN(high) || low >= high) {
        return;
    }
    prev_y_max = high;
    prev_y_min = low;
    if (lock_y_checkbox.checked) {
        // don't need to do anything
    } else {
        lock_y_checkbox.checked = true;
        lock_y_change_callback();
    }
    prev_y_max = high;
    prev_y_min = low;
    updateChart();
};

var lock_y_checkbox = document.getElementById('lock-y');

var lock_y_change_callback = () => {
    if (lock_y_checkbox.checked) {
        if (fix_y) {
            prev_y_max = global_max;
            prev_y_min = global_min;
        }
        lock_y = true;
        fix_y_checkbox.checked = false;
        fix_y = false;
        fit_y_element.classList.add('invalid');
        fix_y_wrapper.classList.add('invalid');
        fix_y_checkbox.classList.add('invalid');
        fix_y_mask_element.style.display = 'block';
    } else {
        lock_y = false;
        fit_y_element.classList.remove('invalid');
        fix_y_wrapper.classList.remove('invalid');
        fix_y_checkbox.classList.remove('invalid');
        fix_y_mask_element.style.display = 'none';
    }
    // updateChart();
};

lock_y_checkbox.addEventListener('change', lock_y_change_callback);

var lock_graph_checkbox = document.getElementById('lock-graph');
lock_graph_checkbox.addEventListener('change', () => {
    if (lock_graph_checkbox.checked) {
        graph_locked = true;
        chart_element.classList.add('locked');
    } else {
        graph_locked = false;
        chart_element.classList.remove('locked');
    }
});

var reverse_mouse_element = document.getElementById('reverse-mouse');
var reverse_mouse = () => {
    if (reverse_mouse_direction) {
        reverse_mouse_direction = false;
        reverse_mouse_element.innerHTML = "Reverse mouse wheel";
    } else {
        reverse_mouse_direction = true;
        reverse_mouse_element.innerHTML = "Unreverse mouse wheel";
    }
};

var slider_element = document.getElementById('slider-button');
var slider_wrapper = document.getElementById('slider-wrapper');



slider_element.addEventListener('mousedown', () => {
    slider_active = true;
});

var resizing_paddle = document.getElementById('resize-paddle');
var resize_prev_loc = -1;
var prev_wrapper_height = -1;
resizing_paddle.addEventListener('mousedown', () => {
    resizing_paddle_active = true;
    if(precise_mouse_y === -1){
        resize_prev_loc = mouseY;
    } else {
        resize_prev_loc = precise_mouse_y;
    }
});

window.addEventListener('mouseup', () => {
    slider_active = false;
    resizing_paddle_active = false;
});

window.addEventListener('mousemove', () => {
    if (slider_active === false) {
        return;
    }
    var wrapper_range = slider_wrapper.getBoundingClientRect();
    var slider_range = slider_element.getBoundingClientRect();
    var bar_height = wrapper_range.height;
    var bar_left = wrapper_range.left;
    var bar_right = wrapper_range.right;
    var valid_left = bar_left + 0.5 * bar_height;
    var valid_right = bar_right - 0.5 * bar_height;
    var mouse_x = precise_mouse_x;
    if (mouse_x === -1) {
        // for safari
        mouse_x = mouseX;
    }
    var ratio = (mouse_x - valid_left) / (valid_right - valid_left);
    if (ratio < 0) {
        ratio = 0;
    }
    if (ratio > 1) {
        ratio = 1;
    }
    slider_element.style.setProperty('--line-width-ratio', ratio);
    var new_line_width = document.querySelector('main').clientWidth / 300 * 28 / 100 * Math.pow(8, (ratio - 0.5));
    update_line_width_only(new_line_width);
});

window.addEventListener('mousemove', () => {
    var prev_loc = resize_prev_loc;
    var main_element = document.getElementById('main');
    var main_width = main_element.clientWidth;
    if (resizing_paddle_active === false) {
        return;
    }
    var current_mouse_loc = precise_mouse_y;
    if(current_mouse_loc === -1){
        current_mouse_loc = mouseY;
    }
    resize_prev_loc = current_mouse_loc;
    var chart_wrapper = document.getElementById('wrapper');
    var wrapper_height = prev_wrapper_height;
    if(wrapper_height === -1){
        wrapper_height = chart_wrapper.clientHeight / main_width * 100;
    }
    var new_height = wrapper_height + (current_mouse_loc - prev_loc) / main_width * 100;
    prev_wrapper_height = new_height;
    chart_wrapper.style.height = new_height + 'vw';
    set_y_value(y_range_prev_min, y_range_prev_max)
});

var reset_line_width = () => {
    slider_element.style.setProperty('--line-width-ratio', 0.5);
    var new_line_width = document.querySelector('main').clientWidth / 300 * 28 / 100;
    update_line_width_only(new_line_width);
};

var pricise_mouse_event_listener = (event) => {
    // 使用 getCoalescedEvents 获取高精度的鼠标位置
    var coalescedEvents;
    try {
        coalescedEvents = event.getCoalescedEvents();
    } catch (e) {
        document.removeEventListener('pointermove', pricise_mouse_event_listener);
    }
    for (const coalescedEvent of coalescedEvents) {
        const x = coalescedEvent.clientX;
        const y = coalescedEvent.clientY;
        precise_mouse_x = x;
    }
};

document.addEventListener('pointermove', pricise_mouse_event_listener);

var debug_checkbox_element = document.getElementById('debug-mode');
debug_checkbox_element.addEventListener('change', () => {
    if (debug_checkbox_element.checked) {
        document.getElementById('debug-info').style.display = 'block';
        document.getElementById('debug-ph').style.display = 'none';
    } else {
        document.getElementById('debug-info').style.display = 'none';
        document.getElementById('debug-ph').style.display = 'block';
    }
});

var data_points_input = document.getElementById('data-points-input');
var data_points_text = document.querySelector('#y-digits-text.data-points-after');
data_points_input.addEventListener('input', () => {
    var value = data_points_input.value;
    value = parseInt(value);
    if (Number.isNaN(value) || value < 50 || value > 5000) {
        data_points_text.innerHTML = "&nbsp;Invalid";
        data_points_text.style.color = "red";
        return;
    }
    data_points_text.innerHTML = '~ ' + value * 2;
    data_points_text.style.color = "#aaa";
});

data_points_input.addEventListener('focusout', () => {
    var value = data_points_input.value;
    value = parseInt(value);
    if (Number.isNaN(value) || value < 50 || value > 5000) {
        return;
    }
    data_points_text.style.color = "#666";
    window_max = value * 2;
    level = 0;
    viewWindow = fake_window_size;
    while (viewWindow > window_max) {
        viewWindow /= 2;
        level++;
    }
    updateChart();
});


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

// remote_print("Test message");
// console.log("Test message");
document.addEventListener('touchstart', () => {
    // console.log("Touch start");
    remote_print("Touch start");
});

document.addEventListener('touchend', () => {
    // console.log("Touch end");
    remote_print("Touch end");
});

document.addEventListener('touchmove', () => {
    // console.log("Touch move");
    remote_print("Touch move");
});