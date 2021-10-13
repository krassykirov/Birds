const user_input = $("#user-input")
const search_icon = $('#search-icon')
const birds_div = $('#replaceable-content')
const more_photos_div = $('#replaceable-photos')
const audio_div = $('#replaceable-audio')
const edit_div = $('#replaceable-edit-ajax')
const birds_form = $('#create-bird');
const edit_bird_name = $('#edit_bird_name');
const endpoint = 'search'
const delay_by_in_ms = 500
let scheduled_function = false

let ajax_call = function (endpoint, request_parameters) {
	$.getJSON(endpoint, request_parameters)
		.done(response => {
			// fade out the artists_div, then:
			birds_div.fadeTo('slow', 0).promise().then(() => {
				// replace the HTML contents
				birds_div.html(response['html_from_view'])
				// fade-in the div with new contents
				birds_div.fadeTo('slow', 1)
				// stop animating search icon
				search_icon.removeClass('blink')
                $("#search-icon").css("display", "none");
			})
		})
}

user_input.on('keyup', function () {
	const request_parameters = {
		q: $(this).val() // value of user_input: the HTML element with ID user-input
	}
	search_icon.addClass('blink')
    $("#search-icon").css("display", "block");
	// if scheduled_function is NOT false, cancel the execution of the function
	if (scheduled_function) {
		clearTimeout(scheduled_function)
	}
	// setTimeout returns the ID of the function to be executed
	scheduled_function = setTimeout(ajax_call, delay_by_in_ms, endpoint, request_parameters)
})

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
const csrftoken = getCookie('csrftoken');

function csrfSafeMethod(method) {
        // these HTTP methods do not require CSRF protection
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }

$.ajaxSetup({
        beforeSend: function (xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
 });

// $(document).ready(function() {
//      $(document).on('click', function (event) {
//         event.preventDefault();
//         // console.log($(event.target))
//         console.log($(event.target).attr("data-id"));
//         if ($(event.target)[0].className === "fa fa-thumbs-up" && $(event.target).attr("data-id") !== 'undefined') {
//             console.log($(event.target).attr("data-id"));
//              $.ajax({
//                 url: 'likes/',
//                 type: 'POST',
//                 data: {
//                     bird_id: $(event.target).attr("data-id"),
//                     csrfmiddlewaretoken: csrftoken
//                 },
//                 success: function (response) {
//                     console.log(response)
//                     $(event.target).html(response);
//                 },
//                 error: function (xhr, errmsg, err) {
//                     console.log('error:', err)
//                     console.log(xhr.status + ":" + xhr.responseText)
//                 }
//             });
//         }
//         else {
//              $(document).off('click')
//              $(event.target)[0].click()
//              $(event.target)[0].closest('.img_wrapper').click()
//             console.log($(event.target)[0].closest('.img_wrapper'));
//             $(event.target)[0].closest('.img_wrapper').click()
//         }
//     });
// })

$(document).ready(function() {
    $("i").on('click', function (event) {
        event.preventDefault();
        console.log($(event.target))
        console.log($(event.target).attr("data-id"));
        if ($(event.target)[0].className === "fa fa-thumbs-up" && $(event.target).attr("data-id") !== 'undefined') {
            $.ajax({
                url: 'likes/',
                type: 'POST',
                data: {
                    bird_id: $(event.target).attr("data-id"),
                    csrfmiddlewaretoken: csrftoken
                },
                success: function (response) {
                    // console.log(response['total_likes'],response['liked'])
                    if (response['liked'] === false) {
                       $(event.target).css("color", "white");
                    }
                    else {
                        $(event.target).css("color", "#8ed3e7");
                    }
                    // $(event.target).html(response['total_likes']);
                }
            });
        }
    });
})

$(document).ready(function() {
$('#create-bird').on('submit', function (event) {
        event.preventDefault();
        // console.log($(event.target))
        var formData = new FormData();
        var bird_name = $('#id_bird_name').val()
        formData.append('bird_name', $('#id_bird_name').val());
        formData.append('url', $('#id_url').val());
        formData.append('bird_description', $('#id_bird_description').val());
        formData.append('photo', $('#id_photo')[0].files[0]);
        formData.append('category', $('#id_category').val());
        $.ajax({
            type: 'POST',
            url: 'create_bird/',
            data: formData,
            cache: false,
            processData: false,
            contentType: false,
            enctype: 'multipart/form-data',
            success: function (response) {
                var html = response['html_from_view']
                if (response['success']) {
                    console.log('Successfully Created Bird')
                    window.location.href = response['url_to_bird']
                }
                if (response['error']){
                      console.log("Error!:",response['error'])
                      alert(response['error'])
                      //birds_form.html(html)
                      window.location.href = 'add_bird'
                  }
            },
            error: function (xhr, errmsg, err) {
                console.log('error:', err)
                console.log(xhr.status + ":" + xhr.responseText)
                window.location.href = 'add_bird'
            }
        })
    })
})

$(document).ready(function() {
    $('#upload-image-btn').on('click', function (event) {
        var message_image = document.getElementById('message_image')
        if(message_image){
            message_image.remove()
        }
        document.getElementById('upload-image').reset()
        $('#upload-image-modal').css('display', 'block');
    });
})

$(document).ready(function() {
    $('#upload-image').on('submit', function (event) {
        event.preventDefault();
        var formData = new FormData();
        formData.append('image', $('#id_image')[0].files[0]);
        formData.append('id', $('#bird_id').val());
        // handle multiple files upload
        // $.each($("#id_photo")[0].files, function(i, file) {
        //     data.append("file", file);
        // });
        $.ajax({
            type: 'POST',
            url: 'upload_image/',
            data: formData,
            cache: false,
            processData: false,
            contentType: false,
            enctype: 'multipart/form-data',
            success: function (response) {
                var html = response['html_from_view']
                if (response['success']) {
                        console.log('Successful Image Upload')
                        more_photos_div.html(html)
                        $('#upload-image-modal').css('display','none')
                        document.getElementById('upload-image').reset();
                        //window.location.href = response['url_to_bird']
                     }
                if (response['error']) {
                         console.log('Error response',response['error'])
                         $('#replace-image-ajax').html(html)
                         $('#upload-image-modal').css('display','block')
                         //window.location.href = response['url_to_bird']
                     }
                },
                error: function (xhr, errmsg, err) {
                console.log('error:', err)
               }
            })
        })
    })

$(document).ready(function() {
    $('#upload-audio-btn').on('click', function (event) {
         console.log('upload-audio-btn clicked')
         var message_audio = document.getElementById('message_audio')
         if(message_audio){
            message_audio.remove()
         }
         document.getElementById('upload-audio').reset()
         $('#upload-audio-modal').css('display', 'block')
    });
})

$(document).ready(function() {
    $('#upload-audio').on('submit', function (event) {
        event.preventDefault();
        var formData = new FormData();
        formData.append('song_name', $('#id_song_name')[0].files[0]);
        formData.append('id', $('#bird_id').val());
        $.ajax({
            type: 'POST',
            url: 'upload_audio/',
            data: formData,
            cache: false,
            processData: false,
            contentType: false,
            enctype: 'multipart/form-data',
            success: function (response) {
                console.log('response',response)
                var html = response['html_from_view']
                if (response['success']) {
                    console.log('Successfully uploaded Audio')
                    audio_div.html(html)
                    $('#upload-audio-modal').css('display','none');
                    document.getElementById('upload-audio').reset()
                    // window.location.href = "/birds/"+ $('#bird_id').val();
                   }
                if (response['error']) {
                         console.log('Error:',response['error'])
                         $('#replace-audio-ajax').html(html)
                         $('#upload-audio-modal').css('display','block')
                      }
                  },
            error: function (xhr, errmsg, err) {
                console.log('error:', err)
                console.log(xhr.status + ":" + xhr.responseText)
                document.getElementById('upload-audio').reset();
            }
        })
    })
})

$(document).ready(function() {
    $('#delete-bird-btn').on('click', function (event) {
        console.log('delete-bird-btn clicked')
        $('#delete-bird-modal').css('display', 'block');
    });
})

$(document).ready(function() {
    $('#delete-bird').on('submit', function (event) {
        event.preventDefault();
        $.ajax({
            type: 'POST',
            url: 'delete_bird/',
            data: { 'id': $('#delete_id').val() },
            success: function (response) {
                var html = response['html_from_view']
                if (response['success']) {
                    console.log('Bird has been deleted')
                    window.location.href = "search"
                   }
                if (response['error']) {
                         console.log('Error:',response['error'])
                         $('#delete-bird-ajax').html(html)
                         $('#delete-bird-modal').css('display','block')
                      }
                  },
            error: function (xhr, errmsg, err) {
                console.log('error:', err)
                console.log(xhr.status + ":" + xhr.responseText)
                document.getElementById('upload-audio').reset();
            }
        })
    })
})

$(document).ready(function() {
    $('#edit-btn').on('click', function (event) {
        var message_edit = document.getElementById('message_edit')
        if (message_edit) {
            message_edit.remove()
        }
        $('#edit-bird-modal').css('display', 'block');
    })
})

$(document).ready(function() {
    $('#edit-bird').on('submit', function (event) {
        event.preventDefault();
        console.log('edit-bird submit')
        var formData = new FormData();
        formData.append('id', $('#edit_id').val());
        formData.append('bird_name', $('#id_bird_name').val());
        formData.append('bird_description', $('#id_bird_description').val());
        formData.append('category', $('#id_category').val());
        $.ajax({
            type: 'POST',
            url: 'edit_bird/',
            data: formData,
            cache: false,
            processData: false,
            contentType: false,
            success: function (response) {
                var html = response['html_from_view']
                if (response['success']) {
                    console.log('Bird has been Updated:',html['bird_name'])
                    edit_bird_name.html(html)
                    $('#edit-bird-modal').css('display', 'none');
                    document.getElementById('edit-bird').reset();
                   }
                if (response['error']) {
                         console.log('Error:',response['error'])
                         edit_div.html(html)
                         $('#edit-bird-modal').css('display', 'block');
                         document.getElementById('edit-bird').reset();
                         //window.location.href = response['url_to_bird']
                      }
                  },
            error: function (xhr, errmsg, err) {
                console.log('error:', err)
                console.log(xhr.status + ":" + xhr.responseText)
                document.getElementById('edit-bird').reset();
                //window.location.href = response['url_to_bird']
            }
        })
    })
})

// $(document).ready(function()  {
//   $("#edit-btnn").click(function () {
//     var description = $();
//     $.ajax({
//       url: '/birdname',
//       type: 'get',
//       dataType: 'json',
//       beforeSend: function () {
//         $("#edit-bird-modal").css('display', 'block');
//       },
//       success: function (data) {
//         $("#modal-book.modal-content").html(data.html_form);
//       }
//     });
//   });
// });