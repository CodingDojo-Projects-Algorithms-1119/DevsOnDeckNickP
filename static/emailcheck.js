jQuery(document).ready(function($){
    console.log("keystroke logged")
    $('#email_check').keyup(function(){
        console.log("testing this nonsense out")
        var data = $("#form_check").serialize()   // capture all the data in the form in the variable data
        console.log(data)
        $.ajax({
            method: "POST",   // we are using a post request here, but this could also be done with a get
            url: "/email_check",
            data: data
        })
        .done(function(res){
            $('#invalid').html(res)  // manipulate the dom when the response comes back
        })
    })
})


// $(document).ready(function(){
//     console.log("keystroke logged")
//     $('#email_check').keyup(function(){
//         console.log("testing this nonsense out")
//         var data = $("#new_dev").serialize()   // capture all the data in the form in the variable data
//         console.log(data)
//         $.ajax({
//             method: "POST",   // we are using a post request here, but this could also be done with a get
//             url: "/email_check",
//             data: data
//         })
//         .done(function(res){
//             $('#invalid').html(res)  // manipulate the dom when the response comes back
//         })
//     })
// })
