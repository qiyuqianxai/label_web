// 人脸类内清理前端
g_database_list_json = [];
g_current_id_range_name = "";
g_id_range_name_list_json = [];
g_current_id_index = 0;

g_current_id_del_pics=[];
$(function () {
    // using ajax to get database and camera list
    var dataurl = '/face_beside_get_database_id_range_list/';
    $.ajax({
        url: dataurl,
        type: "GET",
        success: function (data) {
            var json_data = JSON.parse(data);
            // 获取数据库列表
            $.each(json_data['database_list'], function (i, database_name) {
                g_database_list_json.push(database_name);
                // g_database_id_range_dict_json[database_name] = json_data['database_id_range_list'][i]
            });

            $.each(g_database_list_json, function (i, database_name) {
                $("#database_list").append("<option value=" + i + ">数据源：" + database_name + "</option>");
                // 默认加载第一个
                // if (i == 0) {
                //     $("#database_list").val(i);
                // }
                $("#database_list").val("");
            });

        },
        error: function (data) {
            console.log("get_database_id_range_list is wrong")
            console.log(data);
            alert("获取数据库和标注对象序号列表出错，请登陆，或联系管理员...")

        }
    });
    // logic for database change
    $('#database_list').on('change', function(e){
        if (e.originalEvent) {
            var current_database_name = $("#database_list").find("option:selected").text().slice(4);
            get_free_id(current_database_name);
            //console.log('$("#scrollContent").scrollTop(0)')
            $("#scrollContent").scrollTop(0)
        }
    });

});

function get_free_id(current_database_name)
{
    var dataurl='/beside_get_free_id/';
    var data=JSON.stringify({
        current_database_name:current_database_name,//当前的数据库名称
    });

    jQuery(document).ajaxSend(function(event, xhr, settings) {
        function getCookie(name) {
            var cookieValue = null;
            if (document.cookie && document.cookie != '') {
                var cookies = document.cookie.split(';');
                for (var i = 0; i < cookies.length; i++) {
                    var cookie = jQuery.trim(cookies[i]);
                    // Does this cookie string begin with the name we want?
                    if (cookie.substring(0, name.length + 1) == (name + '=')) {
                        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                        // console.log(cookieValue);
                        break;
                    }
                }
            }
            return cookieValue;
        }
        function sameOrigin(url) {
            // url could be relative or scheme relative or absolute
            var host = document.location.host; // host + port
            var protocol = document.location.protocol;
            var sr_origin = '//' + host;
            var origin = protocol + sr_origin;
            // Allow absolute or scheme relative URLs to same origin
            return (url == origin || url.slice(0, origin.length + 1) == origin + '/') ||
                (url == sr_origin || url.slice(0, sr_origin.length + 1) == sr_origin + '/') ||
                // or any other URL that isn't scheme relative or absolute i.e relative.
                !(/^(\/\/|http:|https:).*/.test(url));
        }
        function safeMethod(method) {
            return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
        }

        if (!safeMethod(settings.type) && sameOrigin(settings.url)) {
            xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
        }
    });//发送cookie，验证登录

    $.ajax({
        url:dataurl,
        contentType: "application/json; charset=utf-8",
        data:data,
        type:"POST",
        success:function(data){
            //每次加载时重置一些参数
            var json_data=JSON.parse(data);
            //console.log(json_data);
            var current_id_range = json_data['current_id_range']; // 当前标注人已经完成的标注
            var current_labeler_last_index = json_data['current_labeler_last_index'];// 当前标注人最后标注的位置 ，即当前主类图片序列
            var current_database_name = json_data['current_database_name'];
            var all_id = json_data['all_id'];
            if (current_id_range == "")
            {
                alert("该批数据已全部分配完成！");
                return
            }
            $('#seleted_id_range').val(current_id_range);
            $("#id_list").empty();
            var id_range_start = parseInt(current_id_range.split('--')[0]);
            var id_range_end = parseInt(current_id_range.split('--')[1]);
            g_id_range_name_list_json = all_id.slice(id_range_start, id_range_end + 1);
            $.each(g_id_range_name_list_json, function (i, id_name) {
                $("#id_list").append("<option value=" + i + ">" + i + "/" + g_id_range_name_list_json.length + "</option>");
            });

            $("#id_list").val(current_labeler_last_index);
            $("#history_id").val(current_labeler_last_index);
            g_current_id_range_name = current_id_range;
            get_data_with_index(current_database_name, current_id_range);

            // 监听标注id范围变化事件
            $('#id_list').on('change', function(e){
                if (e.originalEvent) {
                    sec_pic_index = 0;//id变化重置次类图片当前序列
                    bad_num = 0;
                    get_data_with_index(
                        current_database_name,
                        current_id_range,
                    );
                    $("#scrollContent").scrollTop(0)
                }
            })
        },
        error:function(data){
            console.log("get Info is wrong");
            console.log(data);
            alert("获取数据出错，请登陆，或联系管理员!");
            top.location.reload()
        }
    });

}

function get_all_data(
    current_database_name,
    current_id_range_name,
) {
    var dataurl='/face_beside_get_all_data/';
    $.unique(good_result_pics);
    var data=JSON.stringify({
        current_database_name:current_database_name,//当前的数据库名称
        current_id_range_name:current_id_range_name,//当前的标注对象范围
        current_id_index:g_current_id_index,//当前的主类id序号
        current_id_del_pics:g_current_id_del_pics,//主类删除的图片
        current_add_pics: good_result_pics,//从次类加入主类的图片
    });
    //https://code.ziqiangxuetang.com/django/django-csrf.html
    jQuery(document).ajaxSend(function(event, xhr, settings) {
        function getCookie(name) {
            var cookieValue = null;
            if (document.cookie && document.cookie != '') {
                var cookies = document.cookie.split(';');
                for (var i = 0; i < cookies.length; i++) {
                    var cookie = jQuery.trim(cookies[i]);
                    // Does this cookie string begin with the name we want?
                    if (cookie.substring(0, name.length + 1) == (name + '=')) {
                        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                        break;
                    }
                }
            }
            return cookieValue;
        }
        function sameOrigin(url) {
            // url could be relative or scheme relative or absolute
            var host = document.location.host; // host + port
            var protocol = document.location.protocol;
            var sr_origin = '//' + host;
            var origin = protocol + sr_origin;
            // Allow absolute or scheme relative URLs to same origin
            return (url == origin || url.slice(0, origin.length + 1) == origin + '/') ||
                (url == sr_origin || url.slice(0, sr_origin.length + 1) == sr_origin + '/') ||
                // or any other URL that isn't scheme relative or absolute i.e relative.
                !(/^(\/\/|http:|https:).*/.test(url));
        }
        function safeMethod(method) {
            return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
        }

        if (!safeMethod(settings.type) && sameOrigin(settings.url)) {
            xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
        }
    });//发送cookie，验证登录

    $.ajax({
        url:dataurl,
        contentType: "application/json; charset=utf-8",
        data:data,
        type:"POST",
        success:function(data){
            //每次加载时重置一些参数
            good_result_pics.length = 0;//次类好图片列表清空
            g_current_id_del_pics.length = 0;//当前主类图片中待删的图片列表
            var json_data=JSON.parse(data);

            var all_id = json_data['all_id'];
            // 从json_data['current_mot_id_img_url_list']删除图片
            var current_main_img_url_list = json_data['current_main_img_url_list'];//主类图片链接列表
            var current_id_index  = json_data['current_id_index'];//当前主类图片序列
            var current_sec_img_url_list  = json_data['current_sec_img_url_list'];//次类图片链接集合
            var current_labeler_last_index = json_data['current_labeler_last_index'];// 当前标注人最后标注的位置 ，即当前主类图片序列


            g_current_id_index = current_id_index;
            $("#id_list").val(g_current_id_index);
            $("#seleted_id").val("ID_" + g_id_range_name_list_json[g_current_id_index]);

            $("#history_id").val(current_labeler_last_index);
            // 加载主类图片
            add_search_image(current_main_img_url_list);
            // 加载次类图片
            add_query_result_image(current_sec_img_url_list);

        },
        error:function(data){
            console.log("get Info is wrong");
            console.log(data);
            alert("获取数据出错，请登陆，或联系管理员!");
            top.location.reload()
        }
    });
}

function get_data_with_index(
    current_database_name,
    current_id_range_name,
) {
    g_current_id_index = parseInt($('#id_list').val());
    get_all_data(
        current_database_name,
        current_id_range_name,
    )
}

function get_next_id_data(){
    $("#scrollContent").scrollTop(0);

    if (g_id_range_name_list_json.length == 0){
        console.log("还没有获取列表");
        return
    }
    if (parseInt($("#id_list").val()) === g_id_range_name_list_json.length - 1) {
        alert("该批数据集已完成！");
        $("#id_list").val(parseInt($("#id_list").val()))
    }else{
        $("#id_list").val(parseInt($("#id_list").val()) + 1)
    }

    sec_pic_index = 0;//进入下一组图片时重置次类图片当前序列
    var current_database_name = $("#database_list").find("option:selected").text().slice(4);
    var current_id_range_name = g_current_id_range_name;
    get_data_with_index(
            current_database_name,
            current_id_range_name,
    );
}

// 添加主类图片
function add_search_image(src_set) {
    // 自定义框架
    $('#search_images').html('<div class="pics-wrap col-md-12" id="pics-wrap" style="width:1440px"></div>');
    for(var i=0;i<src_set.length;i++)
    {
        $('#pics-wrap').append('<div class="show_pics col-lg-2" style="display: block; opacity: 1; top: 0px; left: 0px;height: 250px;float: left;align-items: center">' +
            '<img class="img row img-thumbnail" id="main_img_'+i+'" src="'+src_set[i]+'" alt="'+src_set[i]+'" style="width: 88%;height: 85%; margin: 0px;">' +
            '<div class="caption">\n'+
            '      <p>' +
            '           <a href="#" class="del_btn btn btn-danger" role="button" value="'+src_set[i]+'" style="width: 88%;height: 88%">' +
            '                        删除' +
            '           </a> ' +
            '      </p>' +
            '</div>' +
            '</div>');
    }
    // 点击删除按钮后刷新
    $(".del_btn").on("click",function () {
        g_current_id_del_pics.push($(this).attr('value'));
        var current_database_name = $("#database_list").find("option:selected").text().slice(4);
        var current_id_range_name = g_current_id_range_name;
        get_data_with_index(
                current_database_name,
                current_id_range_name,
            );
    })
}

sec_pic_index = 0;// 当前top图片的索引
good_result_pics = [];//保存选中的好质量的图片
bad_num = 0; //记录未选中的图片数量，超过3就提示结束

// 添加次类图片
function add_query_result_image(src_set) {
    // 展示待选择的图片
    show_result_pics(src_set);
    $("#rest_num").text("剩余次类图片数:" + (src_set.length  - sec_pic_index).toString());
    $("#pass_num").text("已放弃图片数:"+bad_num.toString())
}

function show_result_pics(src_set) {
    // 每次显示一张次类图片
    $('#result_pics-wrap').html("")
    if(src_set.length > 0)
    {
        $('#result_pics-wrap').html(
            '       <img class="img img-thumbnail" id="sec_pic" src="'+src_set[sec_pic_index]+'" alt="'+src_set[sec_pic_index]+'" style="width: 88%;height: 88%">' +
            '           <div class="caption">' +
            '              <p>' +
            '                     <a href="#" class="persist_btn btn btn-success" role="button" value="'+src_set[sec_pic_index]+'" style="width: 43%">' +
            '                                  保留' +
            '                     </a> ' +
            '                     <a href="#" class="pass_btn btn btn-danger" role="button" value="'+src_set[sec_pic_index]+'" style="width: 43%">' +
            '                                  放弃' +
            '                     </a> ' +
            '               </p>');
    }
    // 点击保留就把该图片加入到主类
    $(".persist_btn").on("click",function () {
        good_result_pics.push($(this).attr("value"));
        bad_num = 0;
        var current_database_name = $("#database_list").find("option:selected").text().slice(4)
        var current_id_range_name = g_current_id_range_name;
        get_data_with_index(
                current_database_name,
                current_id_range_name,
            );
    });
    // 点击放弃就跳过该图
    $(".pass_btn").on("click",function () {
       bad_num ++;
       if (bad_num === 3)
       {
           bad_num = 0;
           get_next_id_data()
       }
       else {
           sec_pic_index++;
           show_result_pics(src_set);
           $("#rest_num").text("剩余次类图片数:" + (src_set.length  - sec_pic_index).toString());
           $("#pass_num").text("已放弃图片数:"+bad_num.toString())
       }

    });
    // 图片放大
    $(".img").on('click',function(){
        var _this = $(this);//将当前的pimg元素作为_this传入函数
        imgShow("#outerdiv", "#innerdiv", "#bigimg", _this);
    });
}

// 放大图片
function imgShow(outerdiv, innerdiv, bigimg, _this){
    var src = _this.attr("src");//获取当前点击的pimg元素中的src属性
    $(bigimg).attr("src", src);//设置#bigimg元素的src属性
    /*获取当前点击图片的真实大小，并显示弹出层及大图*/

    var windowW = $(window).width();//获取当前窗口宽度
    var windowH = $(window).height();//获取当前窗口高度
    var realWidth = _this.width();//获取图片真实宽度
    var realHeight = _this.height();//获取图片真实高度
    var scale = Math.max(windowW/realWidth,windowH/realHeight);//缩放尺寸，当图片真实宽度和高度大于窗口宽度和高度时进行缩放
    if(scale < 1)
    {
        scale = Math.min(realWidth/windowW,realHeight/windowH);
        scale/=0.4;
        $(bigimg).css({"width":realWidth/scale,"height":realHeight/scale});//以最终的宽度对图片缩放
    }
    else
        {
            scale*=0.4;
            $(bigimg).css({"width":realWidth*scale,"height":realHeight*scale});//以最终的宽度对图片缩放
        }

    var w = (windowW-realWidth*scale)/2;//计算图片与窗口左边距
    var h = (windowH-realHeight*scale)/2;//计算图片与窗口上边距
    $(innerdiv).css({"top":h, "left":w});//设置#innerdiv的top和left属性
    $(outerdiv).fadeIn("fast");//淡入显示#outerdiv及.pimg

    $(outerdiv).click(function(){//再次点击淡出消失弹出层
        $(this).fadeOut("fast");
    });

}


