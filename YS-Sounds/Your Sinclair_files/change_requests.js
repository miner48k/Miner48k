
// Initialize the widget when the DOM is ready
$(function() {
    // Setup html5 version
    $("#uploader").pluploadQueue({
        // General settings
        runtimes : "html5,flash,silverlight,html4",
        url : "/change_requests/upload",

        chunk_size : "1mb",
        rename : true,
        dragdrop: true,

        filters : {
            // Maximum file size
            max_file_size : "250mb",
            // Specify what files to browse for
            mime_types: [
                {title : "Image files", extensions : "jpg,gif,png"},
                {title : "Zip files", extensions : "zip,7z"},
                {title : "PDF files", extensions : "pdf"}
            ]
        },

        // Resize images on clientside if we can
        resize: {
            width : 200,
            height : 200,
            quality : 90,
            crop: true // crop to exact dimensions
        },


        // Flash settings
        flash_swf_url : "/plupload/js/Moxie.swf",

        // Silverlight settings
        silverlight_xap_url : "/plupload/js/Moxie.xap"
    });
});

$(function () {
    $("uploadform").parsley({
        successClass: "has-success",
        errorClass: "has-error",
        errorsWrapper: "<span class='help-block'></span>",
        errorTemplate: "<span></span>",
        classHandler: function (el) {
            return el.$element.closest(".form-group");
        }
    });

    $("#uploadform").parsley().on("form:submit", function (formInstance) {
        var uploader = jQuery("#uploader").pluploadQueue();

        // Files in queue upload them first
        if (uploader.files.length > 0) {
            // When all files are uploaded submit form
            uploader.bind("StateChanged", function() {
                if (uploader.files.length === (uploader.total.uploaded + uploader.total.failed)) {
                    jQuery("#uploadform").parsley().destroy();
                    jQuery("#uploadform").submit();
                    return false;
                }
            });

            uploader.start();
        } else {
            jQuery("#uploadform").parsley().destroy();
            jQuery("#uploadform").submit();
            return false;
        }
        return false;
    });

    $("#uploadform").parsley().on("form:error", function (formInstance) {
        var $tabPane= $(".parsley-error").closest(".tab-pane");
        invalidTabId = $tabPane.attr("id");
        // If the tab is not active
        if (!$tabPane.hasClass("active")) {
            // Then activate it
            $tabPane.parents(".tab-content")
                .find(".tab-pane")
                .each(function(index, tab) {
                    var tabId = $(tab).attr("id"),
                        $li   = $('a[href="#' + tabId + '"][data-toggle="tab"]').parent();

                    if (tabId === invalidTabId) {
                        // activate the tab pane
                        $(tab).addClass("in active");
                        // and the associated <li> element
                        $li.addClass("active");
                    } else {
                        $(tab).removeClass("active");
                        $li.removeClass("active");
                    }
                });
        }
    });
});

/**
 * Contact Form
 */
$(document).ready(function ($) {

    var debug = false; //show system errors

    $('#uploadform').submit(function () {
        var $f = $(this);
        var showErrors = $f.attr('data-show-errors') == 'true';
        var hideForm = $f.attr('data-hide-form') == 'true';
        var $submit = $f.find('[type="submit"]');

        //prevent double click
        if ($submit.hasClass('disabled')) {
            return false;
        }

        $('[name="field[]"]', $f).each(function (key, e) {
            var $e = $(e);
            var p = $e.attr('placeholder');

            //try to geuess placeholder
            if (!p) {
                p = $e.parent().find("label").text();
            }

            if (p) {
                var t = $e.attr('required') ? '[required]' : '[optional]';
                var type = $e.attr('type') ? $e.attr('type') : 'unknown';
                t = t + '[' + type + ']';

                var n = $e.attr('name').replace('[]', '[' + p + ']');

                n = n + t;
                $e.attr('data-previous-name', $e.attr('name'));
                $e.attr('name', n);
            }
        });

        $submit.addClass('disabled');

        $.ajax({
            url: $f.attr('action'),
            method: 'post',
            data: $f.serialize(),
            dataType: 'json',
            success: function (data) {
                $('span.error', $f).remove();
                $('.error', $f).removeClass('error');
                $('.form-group', $f).removeClass('has-error');

                if (data.errors) {
                    $.each(data.errors, function (i, k) {
                        var input = $('[name^="' + i + '"]', $f).addClass('error');
                        if (showErrors) {
                            input.after('<span class="error help-block">' + k + '</span>');
                        }

                        if (input.parent('.form-group')) {
                            input.parent('.form-group').addClass('has-error');
                        }
                    });
                } else {
                    var item = data.success ? '.successMessage' : '.errorMessage';
                    if (hideForm) {
                        $f.fadeOut(function () {
                            $f.parent().find(item).show();
                        });
                    } else {

                        $f.parent().find(item).fadeIn();
                        $f[0].reset();
                    }
                }

                $submit.removeClass('disabled');
                cleanupForm($f);
            },
            error: function (data) {
                if (debug) {
                    alert(data.responseText);
                }
                $submit.removeClass('disabled');
                cleanupForm($f);
            }
        });

        return false;
    });

    function cleanupForm($f) {
        $f.find('.temp').remove();

        $f.find('[data-previous-name]').each(function () {
            var $e = jQuery(this);
            $e.attr('name', $e.attr('data-previous-name'));
            $e.removeAttr('data-previous-name');
        });
    }
});