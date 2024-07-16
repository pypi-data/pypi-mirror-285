
// const webhost = "ws://192.168.31.58:10102/log";
// const host = 'http://' + window.location.host;
// const webhost = 'ws://' + location.hostname + ":9097?debug=true";
var model_show_img = document.getElementById('model_imgshower_img')

var modelObj = null;

$(document).ready(function () {
    model_show_img.onload = function () {
        $("#model_imgshowerimage_loading").hide();
    }
})

function initeditor(module) {
    // init_module_list(module);
    // init_module_pip();
    board_change();
    bind_execboard_move();
    init_bottombar();
    file_menu();
    registerMenu();
    registerKeyCode();
    


}

function init_bottombar(){
    $("#close_consal").click(function(e){
       var dom_exec = $("#exec_board");
       var dom_editor = $("#container");
       var ishide = dom_exec.css("display");
       if(ishide=="none"){
            dom_editor.css("height",dom_editor.attr("lasth"));
            dom_exec.show();
            my_editor.show();
       }else if(dom_exec.height()<40){
            dom_editor.css("height", "75%");
            dom_exec.css("height", "25%");
       }else{
            dom_editor.attr("lasth",dom_editor.height());
            dom_editor.css("height", "100%");
            dom_exec.hide();
            
       }

       my_editor.layout();
    });

    $("#exec_board_clearlog").click(function(e){
        $("#logcontains").empty();
    });

    $("#exec_board_closelog").click(function(e){
        var dom_exec = $("#exec_board");
        var dom_editor = $("#container");
        dom_editor.attr("lasth",dom_editor.height());
            dom_editor.css("height", "100%");
            dom_exec.hide();
            my_editor.layout();
    });


    $("#input_log_filter").bind('input propertychange change',function(){
        var a = $(this).val()

        filterLog(a)

        // if(a.length<1){
        //     $('.log_item').show();
        //     return;
        // }

        
        // $('.log_item').each(function (index,domEle){
        //     // domEle.hide();
        //     var dom = $(domEle).find(".log_item_i,.log_item_e");
        //     var d = dom.text();
        //     var br = $(domEle).attr('b');
        //     if(br=="1"){

        //     }else{
        //         if(d.indexOf(a)>=0){
        //             $(domEle).show();
        //         }else{
        //             $(domEle).hide();
        //         }
        //     }
            
            
            
        //  });

        //  var brs = false;
        //  $('.log_item').each(function (index,domEle){
        //     // domEle.hide();
        //     var ishide = $(domEle).css("display");
        //     if(ishide!="none"){
        //         var b = $(domEle).attr('b');
        //         if(b=="1"){
        //             if(brs== false){
        //                 // alert(1)
        //                 $(domEle).show();
        //                 brs = true;
        //             }else{
        //                 $(domEle).hide();
        //             }
        //         }else{
        //             brs = false;
        //         }
        //     }
        //  });
        //  $(".logitem").each(function(index,domEle){

            // var ishide = $(domEle).css("display");
            // alert(ishide);
            // if(ishide=="none"){
            //     alert('1')
            // }

            // var b = $(domEle).attr('b');
            // if(b=="1"){
            //     --过滤条件去掉重复换行
            //     if(brs){
            //         $(domEle).hide();
            //     }else{
            //         $(domEle).show();
            //     } 
            // }
        //  });


        // alert(a)
    });
}

function bind_execboard_move() {
    var src_posi_Y = 0, dest_posi_Y = 0, move_Y = 0, is_mouse_down = false, destHeight = 0, consleHeight;
    $(".exec_board_title_con")
        .mousedown(function (e) {
            src_posi_Y = e.pageY;
            is_mouse_down = true;
            // addLog("按下"+src_posi_Y);
        });

    $(document).bind("click mouseup", function (e) {
        if (is_mouse_down) {
            is_mouse_down = false;
            my_editor.layout();
        }
    })
        .mousemove(function (e) {
            if (is_mouse_down) {
                dest_posi_Y = e.pageY;
                move_Y = src_posi_Y - dest_posi_Y;
                src_posi_Y = dest_posi_Y;
                destHeight = $("#container").height() - move_Y;
                consleHeight = $(".exec_board").height() + move_Y;
                $("#container").css("height", destHeight);
                $(".exec_board").css("height", consleHeight);
                if(consleHeight<0){
                    // alert("1")
                }
            }
        });


}

function init_module_filelist(module) {
    let filelist_dom = $("#module_files");
    filelist_dom.treeview();
    module_filelist_get(module, filelist_dom);
}

function init_module_list(module) {
    $("#models").hide();
    $.get(`${baseUrl}/api/model/getlist`, function (res) {
        const data = res.data
        data.forEach(e => {
            var item = $("#model_item");
            var nm = item.clone(true);
            nm.find("#model_item_name").text(e.name);
            nm.find("#model_item_time").text(e.lastModified_format);
            nm.find("#model_item_length").text(e.length_format);
            nm.find("#model_rename").attr("data_name", e.name);
            nm.find("#model_delect").attr("data_name", e.name);
            nm.attr("data_name", e.name);

            // nm.find("#model_rename").click(function (e) {
            //     let model_name = $(this).attr("data_name");
            //     e.stopPropagation();
            //     inputmodel("'" + model_name + "' 重命名为", "新的名称", "确定", function (e) {
            //         $.get(host + "/api/model/rename ", {
            //             name: model_name,
            //             rename: $("#input_model_name").val()
            //         }, function (data, textStatus) {
            //             if (data.code == 1) {
            //                 loadModels();
            //                 // $('#modal_success').modal('show')
            //             } else {
            //                 // $('#alert').alert();
            //                 alert(data.msg)
            //             }
            //         }
            //         );
            //     });
            // });
            $("#models").append(nm);
        });
    })
}

function init_module_pip() {
    // $("#pip_packages").hide();
    // alert('1')

    $.get(`${baseUrl}/api/model/pip`, function (res) {
        const data = res.data.install;

        // alert(data.length)

        $("#pip_package_count").text(data.length)

        data.forEach(e => {
            var item = $("#pip_item");
            var nm = item.clone(true);
            nm.find(".pip_itemname").text(e);
            
            $("#pip_packages").append(nm);
        });
    })
}



let module_filecount = 0;

function module_filelist_get(module, dom) {
    dom.empty();

    $.get(`/api/module/files?name=${module}`, function (res) {
        const data = res.data
        modelObj = data;
        if (!data.isFile) {
            $('.module_files_title_namecon_name').text(data.name)
            $("title").html(data.name + " | AScript");
            // $('.file_title').text(`文件(${data.childs.length})`)
        }
        const lists = data.childs
        module_filecount = 0;
        module_filelist_create(lists, dom);
        // alert(module_filecount)
        $('#module_file_counts').text(module_filecount)

        //  ();
    })
}

function module_filelist_create(list, dom) {
    list.forEach(item => {
        if (item.isFile) {
            module_filecount++;
            var fileType = "file";
            // if (item.name.endWith(".lua")) {
            //     fileType = "file_lua"
            // }


            var names = item.name.split(".");
            var branches = $("#file_list_item_model").clone();
            branches.find("#file_list_item_model_type").attr("class", 'file_' + names[names.length - 1]);
            var dom_name = branches.find("#file_list_item_model_name");
            branches.attr("path",item.path);
            dom_name.text(item.name)
            branches.click(function (e) {
                if(item.name.length>2){
                    var reg =/png|jpg|jpeg|gif$/;
                    if(reg.test(item.name.toLowerCase())){
                        showimgModel(item.path)
                        return;
                    }

                    var reg_gp = /gp$/;
                    if(reg_gp.test(item.name.toLowerCase())){
                        // showimgModel(item.path)
                        var gp_url = `${baseUrl}/website/src/screen.html?gp=${item.path}`
                        window.open(gp_url, '_blank');
                        return;
                    }
                }
                editor_createmodule(item);
            });



            branches.appendTo(dom);
            // var branches = $("<li class = 'file'  path = '" + item.path + "'><span class='file_" + names[names.length-1] + "'><a href='javascript:void(0)' style='font-size:small' onClick='getFile(" + item + ")'>" + item.name + "</a></span></li>").appendTo(dom);
            dom.treeview({
                add: branches
            });

            // console.log(item.path)
            if (item.path === modelObj.path+"\\__init__.py") {
                // getFile(item);
                // editor_addmodule(item, my_editor.getModel()); //初次加载,使用editor本身创建的model
                editor_createmodule(item)
            }

        } else {
            var branches = $("<li></li>").appendTo(dom);
            var floder = null;
            if(item.name=="ui"){
                floder = $("<span id='uifolder' class='folder' style='font-size:small' path = '" + item.path + "'>" + item.name + "</span>").appendTo(branches);
            }else{
                floder = $("<span class='folder' style='font-size:small' path = '" + item.path + "'>" + item.name + "</span>").appendTo(branches);
            }
            
            var childcon = $("<ul></ul>").appendTo(branches);
            module_filelist_create(item.childs, childcon)
            dom.treeview({
                add: branches
            });
        }
    });
}

function getUrlParam(variable) {
    var query = window.location.search.substring(1);
    var vars = query.split("&");
    for (var i = 0; i < vars.length; i++) {
        var pair = vars[i].split("=");
        if (pair[0] == variable) { return pair[1]; }
    }
    return (false);
}

function board_change() {
    $("#btn_board_files").click(function (e) {
        $(this).attr("class", "file_nav_hover text-black-50");
        $("#con_moudule_files").show();
        $("#models").hide();
        $("#btn_board_modules").attr("class", "file_nav text-black-50");
    });

    $("#btn_board_modules").click(function (e) {
        $(this).attr("class", "file_nav_hover text-black-50");
        $("#btn_board_files").attr("class", "file_nav text-black-50");
        $("#con_moudule_files").hide();
        $("#models").show();
        // this.attr("class","file_nav_hover text-black-50")
    });
}

function createnewfile(floder,n,t){
    var urlData= {
        path:floder,
        name:n,
        type:t
    };

    $.post(`/api/file/create`, urlData, function (res) {
        init_module_filelist(modelObj.name);
    });
}

function delete_fle(p){
    var urlData= {
        path:p
    };

    $.post(`/api/file/remove`, urlData, function (res) {
        init_module_filelist(modelObj.name);
    });
}

function finder_file(p){
    var urlData= {
        path:p
    };

    $.post(`/api/file/finder`, urlData, function (res) {
        init_module_filelist(modelObj.name);
    });
}

function rename_file(p){
    inputmodel("重命名","文件名称","确定",function(e,v){
        
        var urlData= {
            path:p,
            name:v
        };
    
        $.post(`${baseUrl}/api/file/rename`, urlData, function (res) {
            init_module_filelist(modelObj.name);
        });
    });
}

function res_file(p){
    p = p.replace(modelObj.path,"").substr(1)

    if(p.endsWith(".py")){
        var files = p.split('/')
        var str = `from `
        var fromlj = ""
        for (var i = 0; i < files.length-1; i++) {
            fromlj = fromlj+"."+files[i];
        }

        if(fromlj.length<1){
            fromlj = "."
        }

        str = str+fromlj+" import "+(files[files.length-1].split(".")[0]);
        copy(str)
        return;
    }

    if(p.substr(0,3)=="res"){
        var str = `R(__file__).res('${p.substr(3)}')`;
        copy(str)
    }
}

function file_menu(){
    $("#root_create_newfile").click(function(e){
        inputmodel("新建文件","文件名称","确定",function(e,v){
            if(v.indexOf('.')<0){
                v = v+".py";
            }
            createnewfile(modelObj.path,v,"file")
        });
    });

    $("#root_create_newfolder").click(function(e){
        inputmodel("新建文件夹","文件夹名称","确定",function(e,v){
            createnewfile(modelObj.path,v,"floder")
        });
    });

    $("#root_create_upload").click(function(e){
        uploadFile($("#fileupload"),modelObj.path,function(){
            init_module_filelist(modelObj.name);
        })
    });

    $("#root_create_finder").click(function(e){
        var urlData= {
            path:modelObj.path,
        };

        $.post(`/api/file/finder`, urlData, function (res) {

        });
    });
}

function registerMenu() {

    var foldermenu = {
        // define which elements trigger this menu
        selector: "span.folder",
        // define the elements of the menu
        items: {
          addfile: {
            name: "新建文件", callback: function (key, opt) {
              inputmodel("新建文件","文件名称","确定",function(e,v){
                  if(v.indexOf('.')<0){
                      v = v+".py";
                  }
                  createnewfile(opt.$trigger.attr("path"),v,"file")
              });
            }
          },
          adddir: { name: "新建文件夹", callback: function (key, opt) {
              inputmodel("新建文件夹","文件夹名称","确定",function(e,v){
                  createnewfile(opt.$trigger.attr("path"),v,"floder")
              });
           } },
          upload: { name: "上传文件", callback: function (key, opt) {
               uploadFile($("#fileupload"),opt.$trigger.attr("path"),function(){
                  init_module_filelist(modelObj.name);
               })
              } 
          },
          delete: {
            name: "删除目录", callback: function (key, opt) {
              delete_fle(opt.$trigger.attr("path"), opt.$trigger.text());
            }
          },
          rename: {
            name: "重命名", callback: function (key, opt) {
              rename_file(opt.$trigger.attr("path"));
            }
          },
          finder: {
            name: "在文件夹中打开", callback: function (key, opt) {
              finder_file(opt.$trigger.attr("path"));
            }
          }
        }
        // there's more, have a look at the demos and docs...
    };

    var folderuimenu = $.extend(true,foldermenu);

    folderuimenu.selector = "#uifolder";

    folderuimenu.items["uimaker"] = { name: "UI生成工具", callback: function (key, opt) {
        window.open(`http://ui.ascript.cn`);
    }};

    folderuimenu.items["uimodel"] = { name: "查找UI模版", callback: function (key, opt) {
        window.open(`http://ascript.cn/docs/android/share/ui`);
    }};

    folderuimenu.items["uiexport"] = { name: "UI导出", callback: function (key, opt) {
        // $('#modal_ui_templete').modal('show')
        window.open(`${baseUrl}/api/model/ui/export?name=${modelObj.name}`);
    }};

    folderuimenu.items["uipullin"] = { name: "UI导入(.asui)", callback: function (key, opt) {
        // $('#modal_ui_templete').modal('show')
        uploadUiFile($("#fileupload"),"sdcard/upload",function(res){
            // init_module_filelist(modelObj.name);
            init_module_filelist(modelObj.name);
        },"sdcard/airscript/model/"+modelObj.name+"/res/ui")
    }};

    $.contextMenu(folderuimenu);

    $.contextMenu(foldermenu);

    // uimodel: ,
  
    $.contextMenu({
      // define which elements trigger this menu
      selector: "li.file",
      // define the elements of the menu
      items: {
        delete: {
          name: "删除文件", callback: function (key, opt) {
            delete_fle(opt.$trigger.attr("path"));
          }
        },
        rename: {
          name: "重命名", callback: function (key, opt) {
            rename_file(opt.$trigger.attr("path"));
          }
        },
        rlink: {
          name: "引用", callback: function (key, opt) {
            // , opt.$trigger.text()
            // rename_file(opt.$trigger.attr("path"));
            res_file(opt.$trigger.attr("path"));
          }
        }
      }
      // there's more, have a look at the demos and docs...
    });

    $.contextMenu({
        selector:"#con_moudule_files ",
        // define the elements of the menu
        items: {
          rename: {
            name: "刷新", callback: function (key, opt) {
              // , opt.$trigger.text()
              init_module_filelist(modelObj.name);
            }
          },
          create_file: {
            name: "创建文件", callback: function (key, opt) {
              // , opt.$trigger.text()
              inputmodel("新建文件","文件名称","确定",function(e,v){
                if(v.indexOf('.')<0){
                    v = v+".py";
                }
                createnewfile(modelObj.path,v,"file")
                });
            }
          },
          create_folder: {
            name: "创建文件夹", callback: function (key, opt) {
              // , opt.$trigger.text()
              inputmodel("新建文件夹","文件夹名称","确定",function(e,v){
                createnewfile(modelObj.path,v,"floder")
              });
            }
          },
          upload: {
            name: "上传文件", callback: function (key, opt) {
              // , opt.$trigger.text()
              uploadFile($("#fileupload"),modelObj.path,function(){
                init_module_filelist(modelObj.name);
              })
            }
          }
        }
        // there's more, have a look at the demos and docs...
      });
    
  }


  function showimgModel(url){
    var findpartsrc = `/api/file/get?path=${url}`;
    $('#model_imgshower').modal('show')
    $("#model_imgshowerimage_loading").show();
    model_show_img.src = findpartsrc;

  }

  function registerKeyCode(){
    document.addEventListener('keydown', function(e){
        // alert(e.keyCode)
        if (e.keyCode == 83 && (navigator.platform.match("Mac") ? e.metaKey : e.ctrlKey)){
            e.preventDefault();
            $("#toolbar_save").click();
        }

        if (e.keyCode == 187 && (navigator.platform.match("Mac") ? e.metaKey : e.ctrlKey)){
            // e.preventDefault();
            // alert("+")
        }
    });


    $("#btn_board_quick").click(function(e){
        $("#modal_quick_key").modal('show');
    });

  }


  
