// var timeitem =  $(`<div class ='log_item_con'><span class="log_item"><span style="color:#90959d" ></span>: <span class="log_item_${m.type}">${m.msg}</span></div>`).appendTo($("#logcontains"));


var importTips = [
    "airscript.system.Device",
    "airscript.system.R"
]

$(document).ready(function () {
    // getimportTips();
    
})

function getimportTips(){
    $.post(`${baseUrl}/api/tool/editor/api`, {}, function (res) {
        // alert(res.msg);
        importTips = res.data;
    });
}
    
   
