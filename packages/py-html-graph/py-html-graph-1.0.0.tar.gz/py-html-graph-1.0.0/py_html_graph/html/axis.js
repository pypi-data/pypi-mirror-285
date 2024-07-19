/* 计划 (y坐标值):
   1. 在网页中加入选择和输入框, 可以选择科学记数法或小数, 并输入有效数字位数
   2. 但是暂时先不实现这个, 先按照最简单的实现, 证明可行性
   3. 更高级的方法 (比如去掉几个0、以最小值为基准记录变化量(或百分比)等), 不会考虑, 这应该是用户端的事
   4. 默认 (未选择) 是显示两位小数
 */

const Y_TYPE_UNSELECTED = 11000001;
const Y_TYPE_SCIENTIFIC = 11000002;
const Y_TYPE_DECIMAL = 11000003;

var y_type = Y_TYPE_UNSELECTED;
var y_sci_digits = 3; // 有效位数, 包含小数点前的
var y_dec_digits = 2; // 小数位数

var y_range_prev_min = 0;
var y_range_prev_max = 0;

/* Y 的间距:
   1. 分为 0.1 0.2 0.25 0.5 (*10^n) 等级
   2. 选择可以让间距数大于等于 5 的最大间距 (直接用差除以间距, 不考虑两端、是否显示等因素)
   3. 这样可以保证间距数在 5 - 10 之间
 */

var delete_y_values_scales = () => {
    var y_axis = document.getElementById("y");
    var children = y_axis.children;
    for (var i = children.length - 1; i >= 0; i--) {
        if (children[i].classList.contains('y-js')) {
            y_axis.removeChild(children[i]);
        }
    }
};

var calc_y_interval = (min, max) => {
    var diff = max - min;
    var max_interval = diff / 5;
    var tmp = toScientificNotation(max_interval);
    var main = tmp[0];
    var decimal_digits = tmp[1];
    var l = -1;
    if (main >= 5) {
        l = 5;
    } else if (main >= 2.5) {
        l = 2.5;
    } else if (main >= 2) {
        l = 2;
    } else {
        l = 1;
    }
    var interval = l * Math.pow(10, decimal_digits);
    return interval;
};

var get_chart_height_in_vw = () => {
    var chart = document.getElementById("myChart");
    var height = chart.clientHeight;
    var window_width = document.querySelector('main').clientWidth;
    var vw = height / window_width * 100;
    return vw;
};

var encode_value = (num) => {
    if (y_type === Y_TYPE_UNSELECTED) {
        return num.toFixed(2);
    }
    if (y_type === Y_TYPE_DECIMAL) {
        return num.toFixed(y_dec_digits);
    }
    if (y_type === Y_TYPE_SCIENTIFIC) {
        return num.toExponential(y_sci_digits - 1).replace('+', '');
    }
};

var set_y_value = (min, max) => {
    // document.getElementById('y-top-value').innerHTML = max.toFixed(2);
    // document.getElementById('y-bottom-value').innerHTML = min.toFixed(2);
    // or it will be completely continuous, no space
    document.getElementById('y-top-value').innerHTML = encode_value(max) + '<br>';
    document.getElementById('y-bottom-value').innerHTML = encode_value(min) + '<br>';
    var interval = calc_y_interval(min, max);
    var start = Math.floor(min / interval) + 1;
    var end = Math.floor(max / interval);
    var num = (max - min) / interval;
    if (start * interval - min < interval * 0.5) {
        start += 1
    }
    if (max - end * interval < interval * 0.5) {
        end -= 1
    }
    delete_y_values_scales();
    var height_in_vw = get_chart_height_in_vw();
    var y_axis = document.getElementById("y");
    var offset;
    if (start * interval - min < max - end * interval) {
        offset = -0.75
    } else {
        offset = 0.1
    }
    var bottom_value = document.getElementById('y-bottom-value'); // must put it at last
    y_axis.removeChild(bottom_value);
    for (var i = end; i >= start; i--) {
        // for selection order, use reverse order
        var value = i * interval;
        var distance_to_top = (max - value) / (max - min) * height_in_vw;
        // 刻度线的距离是多少就是多少
        // 数据值的距离, 如果想要在上方, 是 (距离 - 0.75vw), 如果想要在下方, 是 (距离 + 0.1vw)
        var value_element = document.createElement('p');
        var scale_element = document.createElement('div');
        value_element.classList.add('y-value');
        scale_element.classList.add('y-scale');
        value_element.classList.add('y-js');
        scale_element.classList.add('y-js');
        scale_element.style.top = `${distance_to_top}vw`;
        value_element.style.top = `${distance_to_top + offset}vw`;
        value_element.innerHTML = encode_value(value) + '<br>';
        y_axis.appendChild(value_element);
        y_axis.appendChild(scale_element);
    }
    y_axis.appendChild(bottom_value);
    y_range_prev_max = max;
    y_range_prev_min = min;
};

function toScientificNotation(num) {
    const sciString = num.toExponential();
    const [coefficient, exponent] = sciString.split('e');
    const coeffNum = parseFloat(coefficient);
    const expNum = parseInt(exponent);
    return [coeffNum, expNum];
}

var update_y_value = () => {
    if (y_type === Y_TYPE_UNSELECTED) {
        return;
    }
    if (y_digits_input.value.length === 0) {
        return;
    }
    var digits = Number(y_digits_input.value);
    if (Number.isNaN(digits)) {
        return;
    }
    digits = Math.round(digits);
    if (y_type === Y_TYPE_SCIENTIFIC) {
        y_sci_digits = digits + 1;
    }
    if (y_type === Y_TYPE_DECIMAL) {
        y_dec_digits = digits;
    }
    set_y_value(y_range_prev_min, y_range_prev_max);
};

var to_decimal = () => {
    y_type = Y_TYPE_DECIMAL;
    update_y_value();
};

var to_scientific = () => {
    y_type = Y_TYPE_SCIENTIFIC;
    update_y_value();
};

var y_digits_input = document.getElementById('y-digits');
y_digits_input.addEventListener('input', () => {
    // console.log('y_digits_input changed');
    // console.log(y_digits_input.value);
    update_y_value();
});


// ========================= Following is for X axis =========================
const START_UNIX_MS = '$jtc.py-html-graph.x-start-ms$'; // user-configurable
const X_STEP_MS = '$jtc.py-html-graph.x-step-ms$'; // user-configurable
const LEVEL_S = [
    1, 2, 3, 5, 10, 15, 20, 30,
    60, 120, 180, 300, 600, 900, 1200, 1800,
    3600, 3600 * 2, 3600 * 3, 3600 * 4, 3600 * 6, 3600 * 8, 3600 * 12,
    86400, 86400 * 2, 86400 * 3, 86400 * 5, 86400 * 10, 86400 * 15, 86400 * 30,
    86400 * 60, 86400 * 91, 86400 * 122, 86400 * 183, 86400 * 365,
    86400 * 365 * 2, 86400 * (365 * 3 + 1), 86400 * (365 * 5 + 1), 86400 * (365 * 10 + 2)
];
const IDEAL_INTERVAL_NUM = 9;
const WEEK_DAYS = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];

var latest_x_interval_for_encoding_only = 0;

var show_x_week = false;
var x_relative = false;

var get_chart_width_in_vw = () => {
    var chart = document.getElementById("myChart");
    var width = chart.clientWidth;
    var window_width = document.querySelector('main').clientWidth;
    var vw = width / window_width * 100;
    return vw;
};

var find_interval = (diff) => {
    diff = diff / 1000;
    var l = LEVEL_S.length;
    var prev_interval_num = 10000000;
    for (var i = 0; i < l; i++) {
        var interval_num = diff / LEVEL_S[i];
        if (interval_num < IDEAL_INTERVAL_NUM) {
            if (interval_num + prev_interval_num < 2 * IDEAL_INTERVAL_NUM) {
                return LEVEL_S[i - 1];
            } else {
                return LEVEL_S[i];
            }
        }
        prev_interval_num = interval_num;
    }
    return LEVEL_S[l - 1];
};

var delete_x_values_scales = () => {
    var x_axis = document.getElementById("x");
    var children = x_axis.children;
    for (var i = children.length - 1; i >= 0; i--) {
        if (children[i].classList.contains('x-js')) {
            x_axis.removeChild(children[i]);
        }
    }
};

var encode_unix_ms = (num) => {
    num = Math.round(num / 1000) * 1000;
    var date = new Date(num);
    const year = date.getUTCFullYear();     // 获取年份
    const month = date.getUTCMonth() + 1;   // 获取月份，getUTCMonth()返回的是0-11，所以需要+1
    const day = date.getUTCDate();          // 获取日
    const hours = date.getUTCHours();       // 获取小时
    const minutes = date.getUTCMinutes();   // 获取分钟
    const seconds = date.getUTCSeconds();   // 获取秒
    var line1 = `${year}-${month.toString().padStart(2, '0')}-${day.toString().padStart(2, '0')}`;
    var line2 = `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
    if (x_relative) {
        line1 = Math.floor(num / 1000 / 86400) + 'd';
    }
    var time_str = '';
    if (latest_x_interval_for_encoding_only <= 6 * 3600) {
        time_str = line2 + '&nbsp;<br class="no-select">' + line1;
    } else {
        time_str = line1 + '&nbsp;<br class="no-select">' + line2;
    }
    if (x_relative) {
        date = new Date(num + START_UNIX_MS);
    }
    const week = WEEK_DAYS[date.getUTCDay()];
    if (show_x_week) {
        time_str += `&nbsp;<br class="no-select">${week}`;
    }
    return time_str;
};

var set_x_value = () => {
    var min = currentIndex * X_STEP_MS + START_UNIX_MS;
    var max = (currentIndex + fake_window_size) * X_STEP_MS + START_UNIX_MS;
    if (x_relative) {
        min -= START_UNIX_MS;
        max -= START_UNIX_MS;
    }
    var diff = max - min;
    var interval = find_interval(diff) * 1000;
    latest_x_interval_for_encoding_only = Math.round(interval / 1000);
    document.getElementById('x-left-value').innerHTML = encode_unix_ms(min) + '<br>';
    document.getElementById('x-right-value').innerHTML = encode_unix_ms(max) + '<br>';
    var start = Math.floor(min / interval) + 1;
    var end = Math.floor(max / interval);
    var num = (max - min) / interval;
    if (start * interval - min < interval * 0.5) {
        start += 1
    }
    if (max - end * interval < interval * 0.5) {
        end -= 1
    }
    delete_x_values_scales();
    var width_in_vw = get_chart_width_in_vw();
    var x_axis = document.getElementById("x");
    var right_value = document.getElementById('x-right-value'); // must put it at last
    var x_title_element = document.getElementById('x-title');
    x_axis.removeChild(right_value);
    x_axis.removeChild(x_title_element);
    for (var i = start; i <= end; i++) {
        var value = i * interval;
        var distance_to_left = (value - min) / (max - min) * width_in_vw;
        // 刻度线的距离是多少就是多少
        // 数据值的距离, 如果想要在上方, 是 (距离 - 0.75vw), 如果想要在下方, 是 (距离 + 0.1vw)
        var value_element = document.createElement('p');
        var scale_element = document.createElement('div');
        value_element.classList.add('x-value');
        scale_element.classList.add('x-scale');
        value_element.classList.add('x-js');
        scale_element.classList.add('x-js');
        scale_element.style.left = `${distance_to_left - 0.1}vw`;
        value_element.style.left = `${distance_to_left}vw`;
        value_element.innerHTML = encode_unix_ms(value) + '<br>';
        x_axis.appendChild(value_element);
        x_axis.appendChild(scale_element);
    }
    x_axis.appendChild(right_value);
    x_axis.appendChild(x_title_element);
};

var show_x_week_checkbox = document.getElementById('x-week');
show_x_week_checkbox.addEventListener('change', () => {
    if (show_x_week_checkbox.checked) {
        show_x_week = true;
    } else {
        show_x_week = false;
    }
    set_x_value();
});

var x_relative_checkbox = document.getElementById('x-relative');
x_relative_checkbox.addEventListener('change', () => {
    if (x_relative_checkbox.checked) {
        x_relative = true;
    } else {
        x_relative = false;
    }
    set_x_value();
});

var replace_all = (str, a, b) => {
    return str.split(a).join(b);
}

var copy_info = async () => {
    var information = '';
    information += document.getElementById('title').textContent + '\n';
    information += document.getElementById('y-title').textContent + '\n';
    var y_values = document.getElementsByClassName('y-value');
    for (var i = 0; i < y_values.length; i++) {
        information += y_values[i].innerHTML.replace('<br>', '\n');
    }
    for(var i=0;i<VARIABLE_NUM;i++){
        information += replace_all(VARIABLE_NAMES[i], '&nbsp;', ' ') + '\n';
    }
    var x_values = document.getElementsByClassName('x-value');
    for (var i = 0; i < x_values.length; i++) {
        information += x_values[i].innerHTML.replace('&nbsp;<br class="no-select">', ' ').replace('&nbsp;<br class="no-select">', ' ').replace('<br>', '') + '\n';
    }
    information += document.getElementById('x-title').textContent + '\n';
    await navigator.clipboard.writeText(information);
};
