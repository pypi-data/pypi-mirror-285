function waring(title, content, des, btn, fun) {
    $("#modal_sure_waring").text(btn);
    $("#modal_sure_waring").unbind('click').bind('click',fun);
    $("#modal_title_waring").text(title);
    $("#modal_content_waring").text(content);
    $("#modal_des_waring").text(des);

    $('#model_warning').modal('show')
}

function inputmodel(title, des, btn, fun) {
    $('#model_input_title').text(title)
    $('#input_model_name').attr("placeholder", des);
    $('#btn_create_model_mksure').text(btn);
    $('#btn_create_model_mksure').unbind('click').bind('click',function (e) {
        $('#create_model_dialog').modal('hide')
        fun(e,$("#input_model_name").val());
    });
    $('#create_model_dialog').modal('show')
}