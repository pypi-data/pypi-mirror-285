$(document).ready(function () {

getvenvs()
    getdevices()

})


function getvenvs(){
    $.get(`http://127.0.0.1:9097/api/envs`, function (res) {
        if (res.code===1){
            res.data.forEach(e => {
                var item = $(`<option >${e.name}</option>`);

                $("#toolbar_venvs").append(item);
            });
        }else{
            alert(res.msg)
        }
    });
}

function getdevices(){
    $.get(`http://127.0.0.1:9097/api/device`, function (res) {
        if (res.code===1){
            res.data.forEach(e => {
                if(e.statue===0){
                    var item = $(`<option value="${e.Identifier}">${e.DeviceName}(${e.ProductVersion})</option>`);
                    $("#toolbar_devices").append(item);
                }

            });
        }else{
            alert(res.msg)
        }
    });
}
