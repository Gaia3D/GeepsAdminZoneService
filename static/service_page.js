/**
 * Created by jangbi on 2015-06-04.
 */
$(document).ready(onLoad);

var metadata;
var dialog;
var progress;

function onLoad() {
    // 라디오 버튼 채우기
    var class1, class2, timing;
    var table_name;

    var class1_html = '';
    for (var i in metadata) {
        if (class1_html == '') {
            var checked = true;
            class1_html = '<p class="title">자료종류 선택</p>';
        }
        else
            var checked = false;
        class1_html += '<label><input type="radio" name="class1" value="'+i+'"'+(checked?' checked':'')
            +'>'+i+'</label>&nbsp;';
    }
    $("#class1").html(class1_html);
    $('#class1 input:radio').on("change", onSelectedClass1);
    onSelectedClass1()

    // 버튼 동작 부착
    $("button").on("click", onClickButton);

    // progress
    progress = $( "#progressbar" ).progressbar({
      value: 0
    });

    // For IE 9 below, there is no String.trim() function
    if(typeof String.prototype.trim !== 'function') {
        String.prototype.trim = function() {
            return this.replace(/^\s+|\s+$/g, '');
        }
    }
}

function onSelectedClass1() {
    var class1 = $(':radio[name="class1"]:checked').val();
    var class2_dic = metadata[class1];

    if (!class2_dic.length) {
        var class2_html = '';
        for (var i in class2_dic) {
            if (class2_html == '') {
                class2_html = '<p class="title">세부자료 선택</p>';
                var checked = true;
            }
            else
                var checked = false;
            class2_html += '<label><input type="radio" name="class2" value="'+i+'"'+(checked?' checked':'')
                +'>'+i+'</label>&nbsp;';
        }
        $("#class2").html(class2_html);
        $("#class2").show();
        $('#class2 input:radio').on("change", onSelectedClass2);
        onSelectedClass2()
    } else {
        $("#class2").hide();
        onSelectedClass2();
    }
}

function onSelectedClass2() {
    var class1 = $(':radio[name="class1"]:checked').val();
    var class2_dic = metadata[class1];

    var timing_dic;
    if (!class2_dic.length) {
        var class2 = $(':radio[name="class2"]:checked').val();
        timing_dic = class2_dic[class2];
    } else {
        timing_dic = class2_dic;
    }
    var timing_html = '';
    for (var i in timing_dic) {
        if (timing_html == '') {
            timing_html = '<p class="title">자료시기 선택</p>';
            var checked = true;
        }
        else
            var checked = false;
        var timing = timing_dic[i].timing;
        var table_name = timing_dic[i].table_name;
        timing_html += '<label><input type="radio" name="timing" value="'+table_name+'"'+(checked?' checked':'')
            +'>'+timing+'</label>&nbsp;';
    }
    $("#timing").html(timing_html);
    $('#timing input:radio').on("change", onSelectedTiming);
    onSelectedTiming()
}

function onSelectedTiming() {
    var class1 = $(':radio[name="class1"]:checked').val();
    var class2_dic = metadata[class1];
    var class2;

    var timing_dic;
    if (!class2_dic.length) {
        class2 = $(':radio[name="class2"]:checked').val();
        timing_dic = class2_dic[class2];
    } else {
        timing_dic = class2_dic;
    }

    var table_name = $(':radio[name="timing"]:checked').val();
    var timing, agency, source_name, source_url, image_url, description;
    for (var i=0; i<timing_dic.length; i++) {
        var row = timing_dic[i]
        if (row.table_name == table_name) {
            timing = row.timing;
            agency = row.agency;
            source_name = row.source_name;
            source_url = row.source_url;
            image_url = row.image_url;
            description = row.description;
            break;
        }
    }

    if (timing) {
        var title = class1 + (class2 ? ("("+class2+")") : "") + " - " + timing;
        $("#info_title").text(title);
        $("#info_agency").text(agency);
        $("#info_source_name").text(source_name);
        $("#info_source_url").text(source_url);
        $("#info_description").text(description);
        $("#info_image").attr("src", image_url);
    }
}

function onClickButton() {
    var id = $(this).attr("id");

    switch (id) {
        case "run":
            convertAddr();
            break;
        case "btnExport":
            fnExcelReport();
            break;
        default :
            alert(id);
            break;
    }
}

