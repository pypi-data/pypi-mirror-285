// var timeitem =  $(`<div class ='log_item_con'><span class="log_item"><span style="color:#90959d" ></span>: <span class="log_item_${m.type}">${m.msg}</span></div>`).appendTo($("#logcontains"));


function addLog(nstr) {
    
    window.clearTimeout(timeoutId);

    // alert(nstr)
    
    //--内存管理
    // alert($("#logcontains").children().length)

    var log_child_count = $("#logcontains").children().length
    // alert(log_child_count)

    var brcount = $("#logcontains br").length


    var overflow = brcount - 100;

    

    if(overflow>0){
        // alert(overflow);
        // $(".log_item").hide();
        for (var i=0;i<overflow;i++)
        { 
            $("#logcontains").children().first().remove();
            // alert('1')
        }
    }

    var str = logcon.html();
    
    // if (lines.length > 5) {
    //   str = str.substring(lines[0].length + 1, str.length)
    // }
  
    var m = JSON.parse(nstr);

    $(`<span class ="log_item" style="color:#90959d" >${m.time}: </span>:`).appendTo($("#logcontains"));

    $(`<span class="log_item_${m.type}"></span>`).text(m.msg).appendTo($("#logcontains"));
    $(`<br hh='true' />`).last().appendTo($("#logcontains"));

    // if(m.msg.indexOf('\n')>=0){
    //     // 有换行
    //     // alert('1')
    //     var lines = m.msg.split('\n')
    //     for (var i=0;i<lines.length;i++)
    //     {
    //         // 2.当最后一个控件是 br的时候,要加 time
    //         var last_item_dom = $("#logcontains").children().last();
    //
    //         // alert(lines[i].length)
    //         if(lines[i].length>0){
    //             // 1.当log 为空,第一行要加 time
    //             if(last_item_dom.attr("hh")==="true" || log_child_count==0){
    //                 $(`<span class ="log_item" style="color:#90959d" >${m.time}: </span>:`).appendTo($("#logcontains"));
    //             }
    //
    //             $(`<span class="log_item_${m.type}"></span>`).text(lines[i]).appendTo($("#logcontains"));
    //         }
    //
    //         if(i<lines.length-1){
    //             $(`<br hh='true' />`).last().appendTo($("#logcontains"));
    //         }
    //     }
    //
    // }else{
    //     // 没换行
    //
    //     var last_item_dom = $("#logcontains").children().last();
    //
    //     // 3.最后加入 文本信息
    //     if(m.msg.length>0){
    //         // 1.当log 为空,第一行要加 time
    //         if(last_item_dom.attr("hh")=="true" || log_child_count==0){
    //             $(`<span class ="log_item" style="color:#90959d" >${m.time}: </span>`).appendTo($("#logcontains"));
    //         }
    //
    //         $(`<span class="log_item_${m.type}"></span>`).text(m.msg).appendTo($("#logcontains"));
    //     }
    // }

    // 处理没有导包的提示
    if(m.msg && m.msg.length>0){
        // ^NameError: name '(.*)' is not defined$
        var zz ="^NameError: name '(.*)' is not defined\n$"
        res =  m.msg.match(zz);
//        console.log(m.msg + res)
        if(res && res.length==2){
            var tipMsg = ""
//            alert("匹配到了")
            importTips.forEach((item,key) => {
               if(item.endsWith(res[1])){
                tipMsg = "您是否忘记导包了?  from "+ item.replace("."+res[1],"") +" import "+res[1]
                $(`<span class ="log_item" style="color:#90959d" >${m.time}: </span>`).appendTo($("#logcontains"));
                $(`<span class="log_item_s">${tipMsg}</span>`).appendTo($("#logcontains"));
                $(`<br hh='true' />`).last().appendTo($("#logcontains"));
               }
            })

           
        }
    }


    
    // if(m.msg.indexOf('\n')>=0 &&m.msg.length==1){
    //     // alert("换行")
    //     str = str + m.msg;
    // }else{
    //     str = str +`<span class="log_item"><span style="color:#90959d" >${timeStamp2String()}</span>: <span class="log_item_${m.type}">${m.msg}</span></span>`
    // }

    // str = str.replace(/\r\n/g,"<br/>")
    // str = str.replace(/\n/g,"<span class='log_item' b='1'><br/></span>");

    // alert(str);
  
    // logcon.html(str);


    var timestamp = new Date().getTime();
  
    if (timestamp - lastlogupdateTime > 300) {
      var $textarea = $('#logcontains');
      $textarea.scrollTop($textarea[0].scrollHeight);
      lastlogupdateTime = timestamp;
    } else {
      timeoutId = window.setTimeout(function () {
        var $textarea = $('#logcontains');
        $textarea.scrollTop($textarea[0].scrollHeight);
        lastlogupdateTime = timestamp;
      }, 300);
    }
  
}

function timeStamp2String(){ 
    var datetime = new Date(); 
    // datetime.setTime(time); 
    var year = datetime.getFullYear(); 
    var month = datetime.getMonth() + 1 < 10 ? "0" + (datetime.getMonth() + 1) : datetime.getMonth() + 1; 
    var date = datetime.getDate() < 10 ? "0" + datetime.getDate():datetime.getDate(); 
    var hour = datetime.getHours()< 10 ? "0" + datetime.getHours() : datetime.getHours(); 
    var minute = datetime.getMinutes()< 10 ? "0" + datetime.getMinutes() : datetime.getMinutes(); 
    var second = datetime.getSeconds()< 10 ? "0" + datetime.getSeconds() : datetime.getSeconds(); 
    return year + "-" + month + "-" + date+" "+hour+":"+minute+":"+second; 
}

var hasbr = false;

function filterLog(filter){

    $("#logcontains").children().show()
    

    $("#logcontains").children().each(function (index,domEle){
        // domEle.hide();
        if(filter.length<1){
            $("#logcontains").children().show()
        }
        var d = $(domEle).text();
        var br = $(domEle).attr('hh');
        if(d.length>0){
            if(d.indexOf(filter)>=0){
                hasbr = false;
                $(domEle).show();
            }else{
                $(domEle).hide();
            }
        }

        if(br=="true"){
            if(hasbr){
                $(domEle).hide();
            }else{
                hasbr = true;
            }
        }
        
     });
}


// function test(){
//     var zz ="^NameError: name '(.*)' is not defined.*"
//         res =  "NameError: name 'Ocr' is not defined".match(zz);
//         alert(res)

//     // str = "airscript.system.Device"
//     // r =  str.replace(".Device","")
//     // alert(r)
// }

// test();