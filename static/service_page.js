/**
 * Created by jangbi on 2015-06-04.
 */
$(document).ready(onLoad);
var downProcess;
var progressbar;
var progressLabel;
var dialogButtons;
var dialog;
var downloadButton;
var progressTimer;

function onLoad() {
    // 라디오 버튼 채우기
    var class1_html = '';
    var checked;
    for (var i in metadata) {
        if (class1_html == '') {
            checked = true;
            class1_html = '<p class="title">자료종류 선택</p>';
        }
        else
            checked = false;
        class1_html += '<label><input type="radio" name="class1" value="'+i+'"'+(checked?' checked':'')
            +'>'+i+'</label>&nbsp;';
    }
    $("#class1").html(class1_html);
    $('#class1 input:radio').on("change", onSelectedClass1);
    onSelectedClass1();

    // 파일 다운로드하며 Progress 올리기
    // https://jqueryui.com/progressbar/#download
    progressbar = $("#progressbar");
    progressLabel = $(".progress-label");
    dialogButtons = [{
        text: "다운로드 취소",
        click: closeDownload
    }];
    dialog = $("#dialog").dialog({
        autoOpen: false,
        modal: true,
        closeOnEscape: false,
        resizable: false,
        buttons: dialogButtons,
        open: function() {
            //progressTimer = setTimeout(progress, 2000);
            makeZip(progressLabel);
        },
        beforeClose: function() {
            downloadButton.text(" 다운로드 ").prop('disabled', false);
        }
    });
    downloadButton = $("#downloadButton")
        .on("click", function() {
            $(this).text("다운로드 중...").prop('disabled', true);
            dialog.dialog("open");
        });

    progressbar.progressbar({
        value: false,
        change: function() {
            // progressLabel.text("진행상황: " + progressbar.progressbar("value")+"%");
        },
        complete: function() {
            dialog.dialog("option", "buttons", [{
                text: "닫기",
                click: closeDownload
            }]);
        }
    });

    function closeDownload() {
        if (downProcess) downProcess.abort();
        clearTimeout(progressTimer);
        dialog
            .dialog("option", "buttons", dialogButtons)
            .dialog("close");
        progressbar.progressbar("value", false);
        progressLabel.text("Shape 파일 생성중...");
        downloadButton.focus();
    }
}

function onSelectedClass1() {
    var class1 = $(':radio[name="class1"]:checked').val();
    var class2_dic = metadata[class1];

    if (!class2_dic.length) {
        var class2_html = '';
        var checked;
        for (var i in class2_dic) {
            if (class2_html == '') {
                class2_html = '<p class="title">세부자료 선택</p>';
                checked = true;
            }
            else
                checked = false;
            class2_html += '<label><input type="radio" name="class2" value="'+i+'"'+(checked?' checked':'')
                +'>'+i+'</label>&nbsp;';
        }
        $("#class2").html(class2_html).show();
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
    var checked;
    for (var i in timing_dic) {
        if (timing_html == '') {
            timing_html = '<p class="title">자료시기 선택</p>';
            checked = true;
        }
        else
            checked = false;
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
        var row = timing_dic[i];
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

function autoProgress() {
    var val = progressbar.progressbar("value") | 0;
    val = val + Math.floor(Math.random() * 3);
    if (val <= 90) {
        progressbar.progressbar("value", val);
        progressLabel.text("Shape 파일 생성중... " + val +"%");
        progressTimer = setTimeout(autoProgress, 200);
    }
}
function makeZip() {
    var table_name = $(':radio[name="timing"]:checked').val();
    var crs = $('#crs').val().replace("EPSG:", "");

    var current = new Date();
    progressLabel.text("Shape 파일 생성중...");
    progressTimer = setTimeout( autoProgress, 2000 );
    var makeUrl = "./makefile?table_name="+table_name+"&crs="+crs+"&dumy="+encodeURIComponent(current.toString());
    downProcess = $.ajax(makeUrl).done(function(data, textStatus) {
            progressLabel.text("Shape 파일 생성완료. 다운로드 시작중..");
            progressbar.progressbar("value", 100);
            downloadZip(progressLabel);
        }
    ).fail(function( jqXHR, textStatus) {
            progressLabel.text("[오류] "+jqXHR.responseText);
        }
    );
}

function downloadZip() {
    var table_name = $(':radio[name="timing"]:checked').val();
    var crs = $('#crs').val().replace("EPSG:", "");

    var current = new Date();
    var makeUrl = "./download?table_name="+table_name+"&crs="+crs+"&dumy="+encodeURIComponent(current.toString());

    downProcess = $.ajax(
        {
            url: makeUrl,
            type: "GET",
            progress: function (evt) {
                if (evt.lengthComputable) {
                    var val = Math.floor(evt.loaded / evt.total * 100)
                    progressbar.progressbar("value", val);
                    progressLabel.text("다운로드 진행 중... " + val +"%");
                }
                else {
                    progressLabel.text("다운로드 진행 중...");
                }
            }
        }
    ).done(function(data, textStatus) {
            progressLabel.text("다운로드 준비 완료");
            progressbar.progressbar("value", 100);
            // data를 저장할 방법이 없네...
            // iframe을 이용해 별도 창 없이 다운로드
            $iframe = $("<iframe>")
                            .hide()
                            .prop("src", makeUrl)
                            .appendTo("body");
        }
    ).fail(function( jqXHR, textStatus) {
            progressLabel.text("[오류] "+jqXHR.responseText);
        }
    );
}


// add XHR2 upload and download progress events to jQuery.ajax
// IE는 안됨
// https://gist.github.com/nebirhos/3892018
(function addXhrProgressEvent($) {
    var originalXhr = $.ajaxSettings.xhr;
    $.ajaxSetup({
        xhr: function() {
            var req = originalXhr(), that = this;
            if (req) {
                if (typeof req.addEventListener == "function" && that.progress !== undefined) {
                    req.addEventListener("progress", function(evt) {
                        that.progress(evt);
                    }, false);
                }
                if (typeof req.upload == "object" && that.progressUpload !== undefined) {
                    req.upload.addEventListener("progress", function(evt) {
                        that.progressUpload(evt);
                    }, false);
                }
            }
            return req;
        }
    });
})(jQuery);