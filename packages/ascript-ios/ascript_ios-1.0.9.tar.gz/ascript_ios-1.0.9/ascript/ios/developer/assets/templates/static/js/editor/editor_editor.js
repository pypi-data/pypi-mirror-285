const { editor } = require("monaco-editor");

var my_editor = null;
var modalsMap = new Array();//装页面标签的map
var logcon = null;
var lastlogupdateTime = 0;
var timeoutId = 0;
var maxlength = 3;
var editorconfig;

function initeditorcore(name) {
    initToolBar(name);
    require.config({ paths: { vs: './static/libs/monaco/min/vs' } });
    require(['vs/editor/editor.main'], function () {
        modalsMap = [];
        init_module_filelist(name);
        my_editor = monaco.editor.create(document.getElementById('container'), {
            // 版权所属：https://fizzz.blog.csdn.net
            language: 'python'
        });

        // init_config()

        // my_editor.setValue("123")

    });

    websocket();
}


// 创建一个新的model,判断是否已存在model
function editor_createmodule(fm){

    // alert(modalsMap.length)
    //保存当前的model 与 状态
    var currentState = my_editor.saveViewState();
    var currentModel = my_editor.getModel();
    var fmData = null;
    
    modalsMap.forEach((item,key) => {
        if (currentModel === item.model) {
            item.state = currentState;
            item.model = currentModel;
            item.content = currentModel.getValue();
        }

        // alert(fm.path)

        if(fm.path == item.file.path){
            fmData = item;
        }

    });

    if(fmData){

        if(fmData.model.isDisposed()){
            fmData.model = monaco.editor.createModel(fmData.content, "python");
        }

        fmData.model.onDidChangeContent(e => {
            // alert(e)
            fmData.dom.find("#filepannel_item_nosave").show();
        });

        my_editor.setModel(fmData.model);
        my_editor.restoreViewState(fmData.state);
        
        my_editor.focus();

        fmData.dom.siblings().attr("class","con_file_title_board_item_n");
        fmData.dom.attr("class","con_file_title_board_item")

    }else{
        var newModel = null;
        if(modalsMap.length<1){
            newModel = my_editor.getModel();
        }else{
            newModel = monaco.editor.createModel("", "python");
        }

        my_editor.setModel(newModel);

        editor_addmodule(fm,newModel);
    }

}

function saveDataToFile(fmData,callback){
    
    var urlData= {
        path:fmData.file.path,
        content:fmData.content
    };

    $.post(`/api/file/save`, urlData, function (res) {
        // alert(res.msg);
        fmData.dom.find("#filepannel_item_nosave").hide();
        if(callback){
            callback(res);
        }

    });

    // var formData = new FormData();

    // formData.append("path",fmData.file.path);
    // formData.append("content",fmData.content);

    // alert("");

    // $.ajax({
    //     url : `${host}/api/file/save`,
    //     type : "POST",
    //     dataType : 'json',
    //     data : formData,
    //     processData: false,
    //     contentType: false,
    //     success:function (data) {
    //        alert(1);
    //     }
    // });
}


//-如果现有model增加一个model
function editor_addmodule(item,modal){
    var t_pannel = $("#filepannel_item").clone();
    t_pannel.find("#filepannel_item_name").text(item.name);
    t_pannel.appendTo($("#con_file_title_board"));
    t_pannel.attr("title",item.path)
    t_pannel.attr("path",item.path)
    t_pannel.click(function(e){
        editor_createmodule(item);
        $(this).siblings().attr("class","con_file_title_board_item_n");
        $(this).attr("class","con_file_title_board_item")
    });

    t_pannel.find(".con_file_title_board_item_i").click(function(e){
        //关闭文件标签头

        var ishow = t_pannel.find("#filepannel_item_nosave").css("display");
        //--文件没有保存
        if(ishow!="none"){
            alert(0);
            waring("文件内容可能丢失","${item.name} 有内容没有保存","如果您不保存,修改的部分内容将被丢失","确定",function(e){});
        }


        e.stopPropagation(); //阻止传递事件
        if(modalsMap.length>1){
            let d_p = t_pannel.prev();
            let d_n = t_pannel.next();
            t_pannel.remove(); //--移除当前的元素
            var rkey = -1;
            modalsMap.forEach((item,key) => {
                if (t_pannel.attr("path") === item.file.path) {
                    rkey = key;
                    item.model.dispose();
                }
            });

            modalsMap.splice(rkey,1)

            //展示最后一个文件
            if(d_p){
                d_p.click();
            }else if(d_n){
                d_n.click();
            }
            
        }

        
    })

    t_pannel.siblings().attr("class","con_file_title_board_item_n");

    

    $.get(`/api/file/get?path=${item.path}`, function (res) {
        modal.setValue(res);

        modal.onDidChangeContent(e => {
            // alert(e)
            t_pannel.find("#filepannel_item_nosave").show();
        });
        
        var data = {
            file:item,
            model:modal,
            state:null,
            iswhow:true,
            content:res,
            dom:t_pannel
        }

        modalsMap.push(data);
    })

              
}

function editor_getfileContent(item) {
   

}


// -----toolbar

function save_all_and_start(pos,name){
    if(pos<modalsMap.length){
        // alert("222")
       var cm = modalsMap[pos];
       var ishow = cm.dom.find("#filepannel_item_nosave").css("display");
       if(ishow!=="none"){
            cm.content = cm.model.getValue();  
            saveDataToFile(cm,function(){
                save_all_and_start(pos+1,name);
            });
       }else{
            save_all_and_start(pos+1,name);
       }
    }else{
        // alert("?")
        var cdevice =$("#toolbar_devices").val();
        var cvenv = $("#toolbar_venvs").val();
        $.get(`/api/module/run?name=${name}&device=${cdevice}&venv=${cvenv}`, function (res) {
            
        })
    }


}

function initToolBar(name) {
    $("#toolbar_save").click(function (e) {
        var currentModel = my_editor.getModel();
        var fmData = null;
        modalsMap.forEach((item,key) => {
            if (currentModel === item.model) {
                fmData = item;
            }
        });
        fmData.content = fmData.model.getValue();   
        saveDataToFile(fmData);
    });

    $("#toolbar_run").click(function(e){
        // if(editorconfig.autoclear){
        //     $("#logcontains").empty();
        // }

        save_all_and_start(0,name);
    });

    $("#toolbar_stop").click(function(e){
        $.get(`/api/module/stop`, function (res) {
            
        })
    });

    $("#toolbar_export").click(function(e){

        var win = window.open(`${baseUrl}/api/model/export?name=${modelObj.name}`,"load");

        // setTimeout(function(){
        //     // win.document.writeln(`<div style="color: #ff5722;text-align:center;width: 100%"><h1>请勿走开即将跳转.</h1></div>`)
        //     window.open("http://py.airscript.cn/admin/apply/list/create","load");
        // },2000)



    });

    $("#toolbar_export_plug").click(function(e){

            var win = window.open(`${baseUrl}/api/model/exportplug?name=${modelObj.name}`,"load");

            // setTimeout(function(){
            //     // win.document.writeln(`<div style="color: #ff5722;text-align:center;width: 100%"><h1>请勿走开即将跳转.</h1></div>`)
            //     window.open("http://py.airscript.cn/admin/apply/list/create","load");
            // },2000)



        });

    $("#toolbar_viewtree").click(function () {
        var udid = $("#toolbar_devices").val()
        var url = "./vtree.html?device_id="+udid;
        window.open(url);
    });

    $("#toolbar_screen").click(function () {
        var url = "./screen.html?plug=FindColors";
        window.open(url);
    });

    $("#toolbar_colors").click(function () {
        var url = "./colors.html";
        window.open(url);
    });

    $("#btn_codehelper").click(function(e){
        $('#codehepler').modal('show')
    });

    $("#btn_board_theme").click(function(e){
        $('#modal_theme').modal('show')
    });

    $("#editor_theme").change(function(e){
        var module = $("#editor_theme").find("option:selected").text();
        monaco.editor.setTheme(module);
        editorconfig.editor_theme = module;
        save_config();
        
    });

    $("#editor_font_size").change(function(e){
        var module = $("#editor_font_size").find("option:selected").text();
        let options = {"fontSize": module}
        editorconfig.editor_fontsize = module;
        my_editor.updateOptions(options);
        save_config();
    });

    $("#add_newlib").click(function(e){
        window.open(`http://www.airscript.cn/aspip.html`);
    });

    $("#toolbar_ui_gen").click(function(e){
        window.open(`http://ui.ascript.cn/`);
    });

    $("#toolbar_plug_center").click(function(e){
        window.open(`http://ascript.cn/docs/android/api/plug/pluglist`);
    });

    $("#run_clear").change(function(e){
        editorconfig.autoclear = $("#run_clear").prop("checked")
        save_config();
    });

    $(".file_refresh").click(function(e){
        init_module_filelist(getUrlParam("module"));
    })





    // $("#root_create_newfile").click(function () {
    //     var url = "./colors.html?type=4";
    //     window.open(url);
    // });
}

function websocket() {

    let webhost = "ws://"+window.location.hostname+":9098"

    // alert(webhost)

    sock = new ReconnectingWebSocket(webhost);
    sock.onopen = function (e) {
        if (logcon == null) {
            logcon = $("#logcontains");
            logcon.empty();
        }
        $("#exec_board_title_menu_out").attr("class","exec_board_title_menu_item_connect");
    };
    sock.onmessage = function (e) { 
    //   alert(e.data)
      if (logcon == null) {
        logcon = $("#logcontains");
      }
      // console.log(e)
      addLog(e.data);
    };

    sock.addEventListener("close", () => {
        // alert('1')
        $("#exec_board_title_menu_out").classList.remove("exec_board_title_menu_item_connect");
    });

}





function init_config() {
    $.get(`${baseUrl}/api/tool/config/get`, function (res) {
        editorconfig = res.data;

        $("#editor_theme").val(editorconfig.editor_theme);
        monaco.editor.setTheme(editorconfig.editor_theme);

        $("#editor_font_size").val(editorconfig.editor_fontsize);
        let options = {"fontSize": editorconfig.editor_fontsize}
        my_editor.updateOptions(options);

        $("#run_clear").prop("checked",editorconfig.autoclear);
        

    })
}


function save_config() {
    $.post(`${baseUrl}/api/tool/config/save`,{config:JSON.stringify(editorconfig)},function(result){
        // $("span").html(result);
    })
}


function copy(copyTxt) {
    var createInput = document.createElement("input");
    createInput.value = copyTxt;
    document.getElementById("toolbar_save").appendChild(createInput);
    createInput.select();
    document.execCommand("Copy");
    createInput.className = 'createInput';
    createInput.style.display = "none";
}
