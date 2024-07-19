// const baseUrl = 'http://' + window.location.host
// const baseUrl = 'http://192.168.31.59:9096'
let zNodes = null // 树结构信息
let zNodes_cache = null
let nodeIdCount = 1
let doms = []
let modelConfig = null // 手机配置
let scrollTop = 0 // 页面滚动距离
let find_type = 1 //0 找一个,1找全部
let cAppname;
let cActivity;
let cPackageName;

let xDpi = 1
let yDpi = 1
let moveTime;
let selector_str = 0


let model_checks = ["p_add_label", "p_add_value", "p_add_type", "p_add_enabled", "p_add_visible", "p_add_accessible", "p_add_index", "p_add_xpath","p_add_click","p_add_scroll","p_add_input"];

let model_checksString = ["p_add_type","p_add_xpath","p_add_input"];

let model_input =["p_i_label"]


let repetKey = ["parent", "child", "brother"];

var mapSelector = new Map();

var selector = {
  sels: {},
  find: 0
}

$(document).ready(function () { // 初始化
  // var tmode = getmode();
  // if (tmode == 0) {
  //   $("#a_mode_0").addClass("active")
  //   $("#a_mode_1").removeClass("active")
  //   // $("#a_mode_filter_system").prop('checked', false);
  // }else{
  //   $("#a_mode_1").addClass("active")
  //   $("#a_mode_0").removeClass("active")
  //   // $("#a_mode_filter_system").prop('checked', false);
  // }

  var tactivity = getactivity();
  if(tactivity==2){
    $("#a_mode_filter_system").prop('checked', true);
  }else{
    $("#a_mode_filter_system").prop('checked', false);
  }

  $("#a_mode_filter_system").change(function() {  
    var url = window.location.host + window.location.pathname;

    if ($(this).is(':checked')) {  
      // alert(url)
      window.open(`${baseUrl}/website/src/vtree.html?mode=${getmode()}&activity=2`,'_self');
    } else {  
      window.open(`${baseUrl}/website/src/vtree.html?mode=${getmode()}`,'_self');
    }  
    
  });  


  initTreeView("") // 初始化树结构

  attr_change_logic();


});

function attr_change_logic() {
  $(".p_attr_input,#p_m_scroll").on('blur',function () {
      change_selector_values()
  })
  $("#p_m_value,#p_m_label,.p_m_scroll,.p_m_click").change(function () {
    change_selector_values()
  })
}

function getQueryString(name) {
  var reg = new RegExp('(^|&)' + name + '=([^&]*)(&|$)', 'i');
  var r = window.location.search.substr(1).match(reg);
  if (r != null) {
    return unescape(r[2]);
  }
  return null;
}

function getmode() {
  var strm = getQueryString("mode");
  if (strm == undefined || strm.length < 0 || strm == "0") {
    return 0;
  } else {
    return strm;
  }

}

function getactivity() {
  var strm = getQueryString("activity");
  if (strm == undefined || strm.length < 0 || strm == "0") {
    return 0;
  } else {
    return strm;
  }

}

function fill_tree_ui(zNodes) {
  var zTreeObj;
  // zTree 的参数配置，深入使用请参考 API 文档（setting 配置详解）
  var setting = {
    view: {
      addDiyDom: addDiyDom,  //自定义
    },
    data: {
      key: {
        children: 'children',
        name: 'tag'
      }
    }
  };
  // zTree 的数据属性，深入使用请参考 API 文档（zTreeNode 节点数据详解）
  // if (str.length > 0) {
  //   zNodes = res.data
  //   nodeIdCount = res.data.length;
  // } else {
  //   zNodes = [formatZnodesXml(res.documentElement, "/")] // 格式化数据
  //   modelConfig = {}
  //   modelConfig.noncompatHeightPixels = zNodes[0].height
  //   modelConfig.noncompatWidthPixels = zNodes[0].width
  // }

  // alert(zNodes)
  $("#header_total_number").text(`${nodeIdCount}`)
  $("#current_sel_result_count").text(`共找到${zNodes.length}个控件`)
  $(".phone-box").remove();
  zTreeObj = $.fn.zTree.init($("#treeDemo"), setting, zNodes);
  zTreeObj.expandAll(true);
  // 更新页面信息
  // setInfoData()
  // 获取手机截屏
  setCellphoneScreenImg()
}

function initTreeView(str) { // 获取 tree 结构

  // alert(getQueryString("mode"))
  var query_id = getQueryString("device_id")
  if(query_id === undefined){
    alert("没有找到device_id")
    return ;
  }

  let param_data = { device_id: getQueryString("device_id")}

  if(str.length>0){
    param_data["selector"] = str
  }

  $(".node_loading").show()

  $.ajax({
    url: `/api/node/dump`,
    type: 'get',
    data: param_data,
    async: true,
    success: function (res) {
      // alert(res)
      // zNodes_cache = null;


      // modelConfig = res.data.config.display
      // cAppname = res.data.config.appName;
      // cActivity = res.data.config.currentPage;
      // cPackageName = res.data.config.packageName;
      // $("#header_app_name").text(cAppname)
      // $("#header_view").text(cActivity)
      // $("#packge_view").val(cPackageName)
      // $("#header_app_name")[0].innerHTML = `应用${cPackageName}`
      // alert(cAppname+":"+cActivity+":"+cPackageName)


      if (str.length > 0) {
        zNodes = res.data
        // nodeIdCount = res.data.length;
        fill_tree_ui(zNodes);
        $('#sel_result').show();
      } else {
        nodeIdCount = 0;
        doms = []
        zNodes = [formatZnodesXml(res.documentElement, "/")] // 格式化数据
        zNodes_cache = JSON.parse(JSON.stringify(zNodes));
        modelConfig = {}
        modelConfig.noncompatHeightPixels = zNodes[0].height
        modelConfig.noncompatWidthPixels = zNodes[0].width
        fill_tree_ui(zNodes_cache);
      }

      $(".node_loading").hide()


    },
    error: function (err) {
      // console.log('err', err)
      alert(err)
      $(".node_loading").hide()
      bootoast.toast({
        message: 'view 数据获取失败，请刷新尝试',
        type: 'info',
        position: 'right-bottom',
        icon: "ok-sign",
        timeout: 2,
        animationDuration: 300,
        dismissible: true
      });
    }
  })
};

function setInfoData() {
  // alert('1')
  $('#header_pixels').text(`${modelConfig.widthPixels} * ${modelConfig.heightPixels}`)
}

function addDiyDom(treeId, treeNode) {
  var spantxt = $("#" + treeNode.tId + "_span").html();
  // var dom = doms[treeId]
  // console.log(doms[treeNode.nodeId-1])


  if (treeNode.clickable) {
    var clickDom = document.createElement("div");
    clickDom.innerHTML = spantxt
    clickDom.classList.add("click-btn")
    clickDom.classList.add("bg-gradient-success")
    clickDom.id = 'treenode_' + treeNode.nodeId
    // clickDom.onclick = function () {
    //   handleNodeDialog(treeNode)
    //   event.stopPropagation();
    // }
    $("#" + treeNode.tId + "_span").html(clickDom);
  }

  // if(spantxt=="ImageView"){
  //   // var typeDom = $('<i data-feather="menu"></i>');
  //   $("#" + treeNode.tId + "_span").html('<i data-feather="menu"></i>');
  // }

  if (treeNode.name || treeNode.label) {
    let labelStr = treeNode.name || treeNode.label
    if (labelStr.length > 17) {
      labelStr = labelStr.slice(0, 17) + '...'
      // labelStr.length = 17
    }
    var spanDom = document.createElement("span");
    spanDom.style = "display: inline-block;margin-left: 10px;color: #748094;";
    spanDom.innerHTML = labelStr
    $("#" + treeNode.tId + "_span")[0].appendChild(spanDom);
  }

  var detailDom = document.createElement("span");
  detailDom.innerHTML = ''
  detailDom.id = 'detail_btn_' + treeNode.nodeId
  detailDom.classList.add("details")
  detailDom.onclick = function () {
    clickTreeNode(treeNode)
    event.stopPropagation();
  }

  $("#" + treeNode.tId + "_span")[0].onclick = function () {
    clickTreeNode(treeNode)
    event.stopPropagation();
  }

  $("#" + treeNode.tId + "_span")[0].onmouseover = function () {
    // alert('1')
    $("#" + treeNode.tId + "_span")[0].classList.add("bg-gradient-warning")
    $("#" + treeNode.tId + "_span")[0].classList.add("shadow-dark-lg");
    handleMouseoverTree(treeNode)




    event.stopPropagation();
  }
  $("#" + treeNode.tId + "_span")[0].onmouseout = function () {
    $("#" + treeNode.tId + "_span")[0].classList.remove("bg-gradient-warning");
    $("#" + treeNode.tId + "_span")[0].classList.remove("shadow-dark-lg");
    handleMouseoutTree(treeNode)
    event.stopPropagation();
  }
  $("#" + treeNode.tId + "_span")[0].classList = `tree-node-${treeNode.nodeId}`
  $("#" + treeNode.tId + "_span")[0].appendChild(detailDom);
};

function formatZnodes(list) {
  function deleteEmptyArray(children) {
    children.forEach(item => {
      item.nodeId = nodeIdCount
      nodeIdCount++
      if (item.childs.length === 0) {
        delete item.childs
      } else {
        formatZnodes(item.childs)
      }
    })
  }
  deleteEmptyArray(list)
  return list
}


function formatZnodesXml(dom,de_path) {
  var item = {}
  item.tag = dom.nodeName
  item.type = dom.nodeName
  item.nodeId = nodeIdCount
  item.name = dom.getAttribute("name")
  item.value = dom.getAttribute("value")
  item.label = dom.getAttribute("label")
  item.enabled = dom.getAttribute("enabled")==="true"
  item.visible = dom.getAttribute("visible")==="true"
  item.accessible = dom.getAttribute("accessible")==="true"
  item.x = Number(dom.getAttribute("x"))
  item.y = Number(dom.getAttribute("y"))
  item.width = Number(dom.getAttribute("width"))
  item.height = Number(dom.getAttribute("height"))
  item.index = Number(dom.getAttribute("index"))
  item.xpath = `${de_path}/${item.type}[${item.index+1}]`
  doms.push(dom)
  // alert(JSON.stringify(item,0,2))

  nodeIdCount++
  var nodes = dom.childNodes
  if(nodes.length>0){
     item.children = []
     for(let i=0; i<nodes.length; i++){
       if (nodes[i].nodeType===1){
         item.children.push(formatZnodesXml(nodes[i],item.xpath))
       }
     }
  }

  // item.xmldom = dom

  return item
}



function setCellphoneScreenImg() {

  var $img = $('#cellphoneScreen')[0]

  $img.src = '/api/screen/capture'
  $img.onload = function () {
    // $('#cellphoneScreen')[0].style.width = modelConfig.noncompatWidthPixels + 'px'
    // $('#cellphoneScreen')[0].style.height = modelConfig.noncompatHeightPixels + 'px'

    var maxHeight = $("#image_container").height() - 25;
    var maxWidth = $("body").width() * 0.3;

    if ($("#image_container").width() > 1) {
      maxWidth = $("#image_container").width() - 20;
    }

    // alert(maxHeight);

    // var img_width = $img.width()
    // var img_height = $img.height()

    // alert(img_width+":"+img_height)



    var bl;
    if (modelConfig.noncompatHeightPixels > modelConfig.noncompatWidthPixels) {
      bl = modelConfig.noncompatHeightPixels / maxHeight
    } else {
      bl = modelConfig.noncompatWidthPixels / maxWidth
    }

    // $('#phoneimgView')[0].style.width = Math.round(modelConfig.noncompatWidthPixels / bl) + 'px'
    // $('#phoneimgView')[0].style.height = Math.round(modelConfig.noncompatHeightPixels / bl) + 'px'

    // alert(modelConfig.noncompatWidthPixels / bl)
    // alert(modelConfig.noncompatHeightPixels / bl)

    $('#cellphoneScreen')[0].style.width = Math.round(modelConfig.noncompatWidthPixels / bl) + 'px'
    $('#cellphoneScreen')[0].style.height = Math.round(modelConfig.noncompatHeightPixels / bl) + 'px'

    $('#image_container')[0].style.width = Math.round(modelConfig.noncompatWidthPixels / bl) + 20 + 'px'
    // $('#image_container')[0].style.height = Math.round(modelConfig.noncompatHeightPixels / bl) + 'px'

    // $('#image_container')[0].style.height =    Math.round(modelConfig.noncompatHeightPixels / bl) + 'px'

    // alert(    $('#image_container')[0].style.width)





    // $('#phoneimgview_board')[0].style.width = Math.round(modelConfig.noncompatWidthPixels / bl) + 'px'
    // $('#phoneimgview_board')[0].style.height = Math.round(modelConfig.noncompatHeightPixels / bl) + 'px'



    xDpi = (modelConfig.noncompatWidthPixels / $('#cellphoneScreen')[0].width)
    yDpi = (modelConfig.noncompatHeightPixels / $('#cellphoneScreen')[0].height)
    forEachNodes(zNodes)

    //-- 对内部的div 进行排序
    phoneBoxSort();

    // alert('1')

    // bind_execboard_move()
    bind_execboard_drag()

    // $('#cellphoneScreen').css("width", "100%");
    // $('#cellphoneScreen').css("height", "100%");

  }

  function func(item, item1) {
    // let awidth = ((item.rect.right - item.rect.left) / xDpi)
    // let aheight = ((item.rect.bottom - item.rect.top) / yDpi)

    // let awidth1 = ((item1.rect.right - item1.rect.left) / xDpi)
    // let aheight1 = ((item1.rect.bottom - item1.rect.top) / yDpi)
    return ($(item).width() * $(item).height()) - ($(item1).width() * $(item1).height());
  }

  function phoneBoxSort() {
    var bs = $(".phone-box");
    bs.sort(func)
    for (var i = 0; i < bs.length; i++) {
      $(bs[i]).css("z-index", bs.length - i);
    }
  }

  //--变大缩小
  function bind_execboard_move() {
    var src_posi_Y = 0, src_posi_X = 0, dest_posi_Y = 0, dest_posi_X = 0, move_Y = 0, is_mouse_down = false, destHeight = 0, destWidth = 0, moveed = false, consleHeight;
    var moveW = 0, moveH = 0;
    // $(".bottom_bar")
    //   .mousedown(function (e) {
    //     src_posi_Y = e.pageY;
    //     src_posi_X = e.pageX;
    //     is_mouse_down = true;
    //     // addLog("按下"+src_posi_Y);
    //   });

    $(document).bind("click mouseup", function (e) {
      if (is_mouse_down) {
        is_mouse_down = false;
        moveed = false;
        $(".phone-box").remove();
        xDpi = (modelConfig.noncompatWidthPixels / moveW)
        yDpi = (modelConfig.noncompatHeightPixels / moveH)
        forEachNodes(zNodes)
        // $("#bottom_bar_change").click();

        // my_editor.layout();
      }
    })
      .mousemove(function (e) {

        if (is_mouse_down) {
          dest_posi_Y = e.pageY;
          dest_posi_X = e.pageX;
          move_X = src_posi_X - dest_posi_X;
          // move_Y = src_posi_Y - dest_posi_Y;

          var width = $("#phoneimgview_board").width() + move_X;
          var height = Math.round(width / (modelConfig.noncompatWidthPixels / modelConfig.noncompatHeightPixels));
          if (width > 100 && width < $("body").width() && height < $("body").height()) {
            moveW = width;
            moveH = height;
            $("#phoneimgview_board").css("width", width);
            $("#phoneimgview_board").css("height", height);
            moveed = true;
          }


          e.preventDefault();



          //
          // $(".exec_board").css("height", consleHeight);
        }
      });


  }

  function bind_execboard_drag() {
    var src_posi_Y = 0, src_posi_X = 0, dest_posi_Y = 0, dest_posi_X = 0, move_Y = 0, is_mouse_down = false, destHeight = 0, destWidth = 0, moveed = false, right = 0, bottom = 0, consleHeight;

    $(".right_bar")
      .mousedown(function (e) {
        is_mouse_down = true;
        src_posi_Y = e.pageY;
        src_posi_X = e.pageX;
        // alert(right);
        right = $("#image_container").width()
        // alert(right);
        // right = Number(right.replace('px', ''));
        // bottom = $("#image_container").css("bottom")
        // bottom = Number(bottom.replace('px', ''));
        // alert(right);

        // addLog("按下"+src_posi_Y);
      });

    $(document).bind("click mouseup", function (e) {
      if (is_mouse_down) {
        is_mouse_down = false;
        moveed = false;
        // setCellphoneScreenImg()
        $(".phone-box").remove();
        setCellphoneScreenImg()
        // $("#bottom_bar_change").click();

        // my_editor.layout();
      }
    })
      .mousemove(function (e) {

        if (is_mouse_down) {
          dest_posi_Y = e.pageY;
          dest_posi_X = e.pageX;
          move_X = dest_posi_X - src_posi_X;
          move_Y = dest_posi_Y - src_posi_Y;

          // alert(right + move_X)
          if (right + move_X > 20) {
            $("#image_container").width(right + move_X + "px");
          }

          // $("#image_container").css("bottom", bottom + move_Y);

          // $(".right_bar").css("right", right+move_X);
          // $(".right_bar").css("bottom", bottom+move_Y);
          // $(".right_bar").css("height", $("#phoneimgview_board").height());

          // $(".bottom_bar").css("right", right+move_X);
          // $(".bottom_bar").css("bottom", bottom+move_Y);

          moveed = true;

          e.preventDefault();





          //
          // $(".exec_board").css("height", consleHeight);
        }
      });


  }

  function forEachNodes(list) {



    // list.sort(func)


    list.forEach(item => {
      var boxDom = document.createElement("div");
      boxDom.classList = 'phone-box'
      boxDom.id = 'imgnode_' + item.nodeId
      boxDom.style.left = (item.x / xDpi) + 'px'

      boxDom.style.top = (item.y / yDpi) + 'px'
      boxDom.style.width = (item.width / xDpi) + 'px'
      boxDom.style.height = (item.height / yDpi) + 'px'
      boxDom.onmouseover = function () {
        boxDom.classList = 'actived-imgnode phone-box shadow-dark-lg'
        $('.tree-node-' + item.nodeId)[0].style.border = '2px solid #fdf263'
        $('.tree-node-' + item.nodeId)[0].classList.add("bg-gradient-warning")
        $('.tree-node-' + item.nodeId)[0].classList.add("shadow-dark-lg")


        let top = $('.tree-node-' + item.nodeId).offset().top - $("#treeDemo").offset().top;

        // alert(top)

        // alert($("#infoboard").height())
        // $("#viewtree_contain").scrollTop(top);

        moveTime = setTimeout("$('#viewtree_contain').scrollTop(" + (top + 10) + ");", 1000);
        // moveTime = setTimeout("$('.view-body').scrollTop(100);", 1000);
        // moveTime = setTimeout("alert(1)", 2000);
        // $(window).animate({scrollTop: '0px'}, 800);
        let x = Math.round(item.x + item.width / 2)
        let y = Math.round(item.y + item.height / 2)
        $('#header_viewcenter')[0].innerHTML = `${x},${y}`
      }
      boxDom.onmouseout = function () {
        clearTimeout(moveTime)
        $('.tree-node-' + item.nodeId)[0].style.border = 'none'
        $('.tree-node-' + item.nodeId)[0].classList.remove("bg-gradient-warning");
        $('.tree-node-' + item.nodeId)[0].classList.remove("shadow-dark-lg");
        boxDom.classList = 'phone-box'
        event.stopPropagation();
      }
      boxDom.onclick = function (e) {
        $('#detail_btn_' + item.nodeId)[0].click()
        e.stopPropagation();
      }
      // if(boxDom.style.left < $('#cellphoneScreen')[0].width){
      $('#phoneimgView')[0].appendChild(boxDom)
      // }

      if (item.children && item.children.length !== 0) {
        forEachNodes(item.children)
      }
    })
  }
}

function handleNodeDialog(treeNode) {
  // url: `${baseUrl}/cmd?a=click&rule={id=${treeNode.id}}`,

  if (treeNode.id == undefined) {
    alert("ID 为空，请尝试用代码点击，或 坐标点击");
    return;
  }


  $.ajax({
    url: `${baseUrl}/cmd?a=click&rule={\"id\":\"${treeNode.id}\"}`,
    type: 'get',
    async: false,
    success: function (res) {
      console.log('res')
    },
    error: function (err) {
      console.log('err', err)
      alert('err', err)
    }
  })
}

function handleMouseoverTree(node) {
  $('#imgnode_' + node.nodeId)[0].classList = 'actived-imgnode phone-box shadow-dark-lg'
  let x = Math.round(node.x + node.width / 2)
  let y = Math.round(node.y + node.height / 2)
  $('#header_viewcenter')[0].innerHTML = `${x},${y}`
}

function handleMouseoutTree(node) {
  let dom = $('#imgnode_' + node.nodeId)[0]
  if (dom){
    dom.classList = 'phone-box'
  }

}

function postclick(id) {
  var xhr = window.XMLHttpRequest ? new XMLHttpRequest : new ActiveXObject('Microsoft.XMLHTTP');
  var url = 'http://' + window.location.host + '/cmd?a=click&rule={"id":"123"}';
  xhr.open('GET', url, true);
  xhr.send(null);
}

function scrool(t, id) {
  var xhr = window.XMLHttpRequest ? new XMLHttpRequest : new ActiveXObject('Microsoft.XMLHTTP');
  var url = 'http://' + window.location.host + '/cmd?a=click&rule={id:"' + id + '"}';
  xhr.open('GET', url, true);
  xhr.send(null);
}

function changeAttrNodeModeAndFillData(msg, id_i, id_c) {
  // id = "#"+id;
  if (msg != null) {
    document.getElementById(id_i).value = msg;
    document.getElementById(id_i).disabled = false;
    if(id_c){
      document.getElementById(id_c).disabled = false;
    }

  } else {
    document.getElementById(id_i).value = "";
    document.getElementById(id_i).disabled = true;
    if(id_c){
      document.getElementById(id_c).disabled = true;
    }
  }
}

function get_attr_with_id(nid){
  $(".node_loading_attr").show()
  let param_data = { device_id: getQueryString("device_id"),node_id:nid}
  $.ajax({
      url: `/api/node/attr`,
      type: 'get',
      data: param_data,
      async: true,
      success: function (res) {
        $(".node_loading_attr").hide()
        res.data.id = null
        clickTreeNode(res.data)

      },
      error: function (err) {
        // console.log('err', err)
        alert(err)
        $(".node_loading_attr").hide()
      }
  })
}

function clickTreeNode(treeNode) {

  // 恢复属性默认
  $(".p_attr_input").val("")
  model_checks.forEach(item => {
    // $("#" + item).change(changeSelectorValue)
      $("#" + item).prop("checked",false)
  })

  $("#p_m_value,#p_m_label").val("0")

  if(treeNode.id){
    // alert("hasid")
    get_attr_with_id(treeNode.id)
    $('#attrView').show()
    $('#attr_close_tip').show()
    return;
  }

  changeAttrNodeModeAndFillData(treeNode.label, "p_i_label", "p_add_label");

  changeAttrNodeModeAndFillData(treeNode.value, "p_i_value", "p_add_value");

  changeAttrNodeModeAndFillData(treeNode.type, "p_i_type", "p_add_type");

  changeAttrNodeModeAndFillData(treeNode.enabled, "p_i_enabled", "p_add_enabled");

  changeAttrNodeModeAndFillData(treeNode.accessible, "p_i_accessible", "p_add_accessible");

  changeAttrNodeModeAndFillData(treeNode.index, "p_i_index", "p_add_index");

  changeAttrNodeModeAndFillData(treeNode.visible, "p_i_visible", "p_add_visible");

  changeAttrNodeModeAndFillData(treeNode.xpath, "p_i_xpath", "p_add_xpath");

  // alert(JSON.stringify(treeNode,0,2))
  let bounds = [treeNode.x,treeNode.y,treeNode.x+treeNode.width,treeNode.y+treeNode.height]
  changeAttrNodeModeAndFillData(bounds.join(","),"p_i_rect",null)

   // document.getElementById("p_i_rect").value = `${treeNode.x},${treeNode.y},${treeNode.x + treeNode.width},${treeNode.y + treeNode.height}`;
  //


  // let dom = doms[treeNode.nodeId-1]

  // alert(dom)

  // console.log(dom)


  // console.log(treeNode)
  // changeAttrNodeModeAndFillData(`${treeNode.x},${treeNode.y},${treeNode.x+treeNode.width},${treeNode.y+treeNode.height}`, "p_i_rect", null);

  // $("#p_i_rect").val()




  // document.getElementById("p_i_page").value = cActivity;
  // document.getElementById("p_i_package").value = treeNode.packageName;
  // document.getElementById("p_i_path").value = treeNode.path;
  // document.getElementById("p_i_childCount").value = treeNode.childCount;
  // document.getElementById("p_i_inputType").value = treeNode.inputType;
  // document.getElementById("p_i_drawingOrder").value = treeNode.drawingOrder;
  // document.getElementById("p_i_depth").value = treeNode.depth;
  // document.getElementById("p_i_maxTextLength").value = treeNode.maxTextLength;
  // document.getElementById("p_i_clickable").value = treeNode.clickable ? 'True' : 'False';
  // document.getElementById("p_i_checkable").value = treeNode.checkable ? 'True' : 'False';
  // document.getElementById("p_i_checked").value = treeNode.checked ? 'True' : 'False';
  // document.getElementById("p_i_editable").value = treeNode.editable ? 'True' : 'False';
  // // document.getElementById("p_i_dismissable").value = treeNode.dismissable;
  // document.getElementById("p_i_longClickable").value = treeNode.longClickable ? 'True' : 'False';
  // document.getElementById("p_i_focusable").value = treeNode.focusable ? 'True' : 'False';
  // document.getElementById("p_i_focused").value = treeNode.focused ? 'True' : 'False';
  // document.getElementById("p_i_visible").value = treeNode.visible ? 'True' : 'False';
  // document.getElementById("p_i_rect").value = `${treeNode.x},${treeNode.y},${treeNode.x + treeNode.width},${treeNode.y + treeNode.height}`;
  //


  $('#attrView').show()
  $('#attr_close_tip').show()

  // $(":not('#attrView')").click(function() {
  //   //点击事件发生后，执行的代码
  //   $('#attrView').hide()
  // });


  // document.getElementById("p_c_click").checked = treeNode.click
  // document.getElementById("p_c_e").checked = treeNode.editor
  // document.getElementById("p_c_sel").checked = treeNode.checked
  // document.getElementById("p_c_s").checked = treeNode.canScroll
  // $("#btn_rule_checked").html("忽略")


  // mapSelector = new Map();
  // $('#p_params').modal('show')

  // tip(document.getElementById("p_i_rect").value);
};


function hideparams() {
  tipClose();
}

function back() {
  window.location.href = 'http://' + window.location.host;
}

function refesh() {
  window.location.reload();
}

function tip(l) {
  var xhr = window.XMLHttpRequest ? new XMLHttpRequest : new ActiveXObject('Microsoft.XMLHTTP');
  var url = 'http://' + window.location.host + '/view/tip?value=' + l;
  xhr.open('GET', url, true);
  xhr.send(null);
}

function tipClose() {
  var xhr = window.XMLHttpRequest ? new XMLHttpRequest : new ActiveXObject('Microsoft.XMLHTTP');
  var url = 'http://' + window.location.host + '/view/tipc';
  xhr.open('GET', url, true);
  xhr.send(null);
}

function checkidvalueisstr(k) {
  var e = false;
  model_checksString.some(item => {
    // alert(k.trim()+"?"+item)
    if (k.trim() == item.trim()) {
      // alert("=")
      e = true;
    }
  });
  return e;
}

var attrid;

function changeattr(e) {

  attrid = $(this).attr("data-id");
  var k = $(this).attr("data-key");
  var v = $(this).attr("data-value");
  // alert(attrid)

  $("#sel_attr_fixer_title").text(k)
  $("#sel_attr_fixer_value").val(v)
  // var nv = prompt(`修改${$(this).attr("data-key")}的值为?`, $(this).attr("data-value"))

  $(".sel_attr_fixer").css("top", $(".attr_footer").offset().top - $(".attr_footer").height() + 10)
  $(".sel_attr_fixer").show(100)

  // alert(nv)



  changeSelectorValue()

  // e.stopPropagation();

}

function sel_attr_item_hover() {
  var attrid = $(this).attr("data-id");
  var attrkey = $(this).attr("data-key");
  // alert(attrkey)
  var ox = $(this).offset().left
  var oy = $(this).offset().top


  $(".sel_attr_fixer").css("left", ox)
  $(".sel_attr_fixer").css("top", oy - 30)

}

function change_selector_values(){
    model_checks.forEach(item => {
      // $("#" + item).change(changeSelectorValue)
      let dom_item = $("#" + item)
      var id = dom_item.attr("id").replace("p_add_", "");
      if(dom_item.is(':checked')){
        var val = $("#p_i_" + id).val();
        var match = $("#p_m_" + id).val();
        if(match){
          match = Number(match)
          if(match===0){
            selector.sels[id] = [val]
          }else{
            selector.sels[id] = [val,match]
          }

        }else{
          if(val==='true' || val==="false"){
            val = JSON.parse(val)
          }
          selector.sels[id] = val
        }
        console.log(selector)
      }else{
        delete selector.sels[id]
      }
    })

    let con_dom = $("#code_container")
    con_dom.empty();
    $(`<a href="#">Selector()</a>`).appendTo(con_dom)

    selector_str = "Selector()"


    Object.keys(selector.sels).forEach(k=>{
      let v = selector.sels[k];
      if (Array.isArray(v)){
        v = JSON.stringify(v).replaceAll("\[","").replaceAll("\]","")
      }

      var vstr = ""
        var needStr = checkidvalueisstr("p_add_" + k);
        if (needStr) {
          vstr = `.${k}("${v}")`
        } else {
          vstr = `.${k}(${v})`
        }

        selector_str = selector_str + vstr
      var nattrDom = $(`<a class"sel_attrs" href="#" data-id="${k}" data-key="${k}" data-value="${v}" >${vstr}</a>`)
      // nattrDom.click(changeattr)
      // nattrDom.hover(sel_attr_item_hover)
      nattrDom.appendTo(con_dom)
    })

    var findstr = ""
    if (find_type === 1) {
      findstr = `.find()`;
    } else {
      findstr = `.find_all()`;
    }

    selector.find = find_type;

    selector_str = selector_str + findstr
    const fDom = $(`<a href="#">${findstr}</a>`);
    fDom.appendTo(con_dom)
}

function changeSelectorValue(e) {
  var idcheck = $(this).attr("id");
  if (idcheck) {
    var id = $(this).attr("id").replace("p_add_", "");
    var checked = $(this).prop("checked");
    // var bind =$(this).attr("bind");
    var val = $("#p_i_" + id).val();
    // alert(typeof value)
    if(checked){
      selector.sels[id] = val
    }else{
      delete selector.sels[id]
    }

  }


  //--组装 selector
  $("#code_container").empty();
  $(`<a href="#">Selector()</a>`).appendTo($("#code_container"))


  Object.keys(selector.sels).forEach(k=>{
    var v = selector.sels[k]
    var vstr = ""
      var needStr = checkidvalueisstr("p_add_" + k);
      if (needStr) {
        vstr = `.${k}("${v}")`
      } else {
        vstr = `.${k}(${v})`
      }
    var nattrDom = $(`<a class"sel_attrs" href="#" data-id="${k}" data-key="${k}" data-value="${v}" >${vstr}</a>`)
    nattrDom.click(changeattr)
    // nattrDom.hover(sel_attr_item_hover)
    nattrDom.appendTo($("#code_container"))
  })

  // selector.sels.forEach((seq, index, arr) => {
  //   // alert(JSON.stringify(seq))
  //   seq.link.forEach(item => {
  //     var k = item.key;
  //     var v = item.value[0];
  //     if (!v) {
  //       v = ""
  //     }
  //     var vstr = ""
  //     var needStr = checkidvalueisstr("p_add_" + k);
  //     if (needStr) {
  //       vstr = `.${k}("${v}")`
  //     } else {
  //       vstr = `.${k}(${v})`
  //     }
  //     var nattrDom = $(`<a class"sel_attrs" href="#" data-id="${item.id}" data-key="${k}" data-value="${v}" >${vstr}</a>`)
  //     nattrDom.click(changeattr)
  //     // nattrDom.hover(sel_attr_item_hover)
  //     nattrDom.appendTo($("#code_container"))
  //   });
  // });

  var findstr = ""
  if (find_type == 1) {
    findstr = `.find()`;
  } else {
    findstr = `.find_all()`;
  }

  selector.find = find_type;

  var fDom = $(`<a href="#">${findstr}</a>`)
  fDom.appendTo($("#code_container"))

}


// $(function () {
//   $('#p_params').on('hide.bs.modal',
//     // function () {
//     //   hideparams();
//     //   $("#p_c_id,#p_c_text,#p_c_desc,#p_c_type,#p_c_childCount,#p_c_name,#p_c_page,#p_c_path").prop('checked', false);
//     //   document.getElementById("p_i_code").value = "";
//     // })
// });

$(function () {
  // $("#p_c_id,#p_c_text,#p_c_desc,#p_c_type,#p_c_childCount,#p_c_name,#p_c_page,#p_c_path").change(changeSelectorValue);

  model_checks.forEach(item => {
    // $("#" + item).change(changeSelectorValue)
    $("#" + item).click(change_selector_values)
  })

  $("#p_b_copy").click(function (e) {
    // alert(document.getElementById("p_i_code").value)
    // copy2(getSelectorStrs());
    copy2(selector_str)
    e.stopPropagation();

  })

  // $("#p_b_close").click(function () {
  //   // alert(document.getElementById("p_i_code").value)
  //   $('#attrView').hide()
  // })

  $("#p_b_clear").click(function (e) {
    // alert(document.getElementById("p_i_code").value)
    selector = {
      sels: {},
      find: 0
    }
    changeSelectorValue();
    // 清空所有勾选的值
    model_checks.forEach(item => {
    // $("#" + item).change(changeSelectorValue)
      $("#" + item).prop("checked",false)
    })


    e.stopPropagation();
  })

  // $("#p_b_findtype").click(function(e){
  //   // alert(1)
  //   $("#find_selector").show()
  //   e.stopPropagation();

  // })

  $("#p_find_one").click(function (e) {
    // alert(document.getElementById("p_i_code").value)
    var selstr = JSON.stringify(selector);
    if (selstr.length > 0) {
      find_type = 1;
      $("#p_b_findtype_des").text("查找一个")
      changeSelectorValue();
    }

    e.stopPropagation();
    return
  })

  $("#p_find_all").click(function (e) {
    // alert(document.getElementById("p_i_code").value)
    var selstr = JSON.stringify(selector);
    if (selstr.length > 0) {
      find_type = 99999;
      $("#p_b_findtype_des").text("查找全部")
      changeSelectorValue();
    }
    e.stopPropagation();
  })

  $("#p_b_try").click(function (e) {
    // alert(document.getElementById("p_i_code").value)
    var selstr = JSON.stringify(selector);
    if (selstr.length > 0) {

      initTreeView(selstr);
      $("#current_sel").text(getSelectorStrs())
      // $('#p_params').modal('hide')

    }
    e.stopPropagation();
  })

  $("#del_selector_res").click(function (e) {
    $('#sel_result').hide();
    zNodes = zNodes_cache
    fill_tree_ui(zNodes);
    // initTreeView("");
    // zNodes = zNodes_cache
    // var setting = {
    //     view: {
    //       addDiyDom: addDiyDom,  //自定义
    //     },
    //     data: {
    //       key: {
    //         children: 'children',
    //         name: 'type'
    //       }
    //     }
    //   };
    // zTreeObj = $.fn.zTree.init($("#treeDemo"), setting, zNodes);
    // zTreeObj.expandAll(true);
    // setCellphoneScreenImg()
    // e.stopPropagation();
  });

  $("#del_selector_copy").click(function (e) {
    copy2($("#current_sel").text());
    e.stopPropagation();
  });

  $("#viewtree_contain,#image_container").click(function () {
    $('#attrView').fadeOut(100)
    $(".sel_attr_fixer").hide(100)
    $("#attr_close_tip").hide()
  })

  $("#attr_close_tip").click(function (e) {
    $('#attrView').fadeOut(100)
    $(".sel_attr_fixer").hide(100)
    $("#attr_close_tip").hide()
  })



  $("#sel_attr_fixer_close").click(function () {
    $(".sel_attr_fixer").hide(100)
  })

  $("#sel_attr_fixer_del").click(function (e) {
    var nvs = []
    selector.sels.forEach((seq, index, arr) => {
      var newseq = []
      seq.link.forEach((item,pos) => {
        if (item.id == attrid) {

        } else {
          newseq.push(item)
        }
      });
      
      seq.link = newseq
      if(seq.link.length>0){
        nvs.push(seq)
      }
    })

    selector.sels = nvs;

    changeSelectorValue();

    $(".sel_attr_fixer").hide(100)

    // e.stopPropagation();

  })

  $("#sel_attr_fixer_submit").click(function (e) {
    var nv = $("#sel_attr_fixer_value").val()
    var nvs = []
    selector.sels.forEach((seq, index, arr) => {

      // console.log(item.id)

      seq.link.forEach(item => {
        if (item.id == attrid) {
          if (nv.length > 0) {
            item.value = [nv];
          } else {
            item.value = [];
          }
        }
      });

      // nvs.push(item)
    });

    // selector.sels = nvs

    changeSelectorValue()

    $("#sel_attr_fixer").hide(100)
  })




  document.addEventListener('keydown', function (e) {
    // alert(e.keyCode)
    if (e.keyCode == 27) {
      // alert("1")
      e.preventDefault();
      $('#attrView').fadeOut(100)
      $(".sel_attr_fixer").hide(100)
      $("#attr_close_tip").hide()
    }

  });




  // const toast = new bootstrap.Toast($("#liveToast"))

  //   toast.show()

  // $().alert()



  function copy(copyTxt) {
    var createInput = document.createElement("input");
    createInput.value = copyTxt;
    document.getElementById("p_params").appendChild(createInput);
    createInput.select();
    document.execCommand("Copy");
    createInput.className = 'createInput';
    createInput.style.display = "none";
  }

  function copy2(copyTxt) {
    var createInput = document.createElement("input");
    createInput.value = copyTxt;
    document.getElementById("con_tools_bar").appendChild(createInput);
    createInput.select();
    document.execCommand("Copy");
    createInput.className = 'createInput';
    createInput.style.display = "none";
  }

  function getSelectorStrs() {

    var mode = Number(getQueryString("mode")) + Number(getactivity())

    if (mode == undefined || mode.length < 0 || mode == "0") {
      mode = ""
    }

    // alert(mode)

    var selectorStr = "Selector(" + mode + ")"

    Object.keys(selector.sels).forEach(k=>{
      var v = selector.sels[k]
      if (v === undefined) {
          v = "";
        }

      var needStr = checkidvalueisstr("p_add_" + k);
        if (needStr) {
          // selectorStr = +v.replace("p_c_","")+'("'
          selectorStr = selectorStr + `.${k}("${v}")`
        } else {
          selectorStr = selectorStr + `.${k}(${v})`
        }
    })

    if (find_type == 1) {
      selectorStr = selectorStr + `.find()`;
    } else {
      selectorStr = selectorStr + `.find_all()`;
    }

    return selectorStr;

  }


});
