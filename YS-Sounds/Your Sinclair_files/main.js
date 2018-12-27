"use strict";


$(document).ready(function(){
	var highestBox = 60;
	$('.eqheight').each(function(){
		if($(this).height() > highestBox){
			highestBox = $(this).height();
		}
	});
	$('.eqheight').height(highestBox);

});

function pieChart() {
	
	//circle progress bar
	if (jQuery().easyPieChart) {
		var count = 0 ;
		// var colors = ['#55bce9', '#7370b5', '#6496cf'];
		var colors = ['#55bce9'];

		jQuery('.chart').each(function(){
			
			var imagePos = jQuery(this).offset().top;
			var topOfWindow = jQuery(window).scrollTop();
			if (imagePos < topOfWindow+900) {

				jQuery(this).easyPieChart({
			        barColor: colors[count],
					trackColor: '#ffffff',
					scaleColor: false,
					scaleLength: false,
					lineCap: 'butt',
					lineWidth: 20,
					size: 270,
					rotate: 0,
					animate: 3000,
					onStep: function(from, to, percent) {
							jQuery(this.el).find('.percent').text(Math.round(percent));
						}
			    });
			}
			count++;
			if (count >= colors.length) { count = 0};
		});
	}
}

//function that initiating template plugins on document.ready event
function documentReadyInit() {
	///////////
	//Plugins//
	///////////
    //contact form processing
	/**
	 * Contact Form
	 */
	jQuery(document).ready(function ($) {
		"use strict";
		$ = jQuery.noConflict();

		var debug = false; //show system errors

		$('.validateIt').submit(function () {
			var $f = $(this);
			var showErrors = $f.attr('data-show-errors') == 'true';
			var hideForm = $f.attr('data-hide-form') == 'true';
			var emailSubject = $f.attr('data-email-subject');
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

			$f.append('<input class="temp" type="hidden" name="email_subject" value="' + emailSubject + '">');

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
    //mailchimp subscribe form processing
    jQuery('.signup').on('submit', function( e ) {
        e.preventDefault();
        var $form = jQuery(this);
        // update user interface
        $form.find('.response').html('Adding email address...');
        // Prepare query string and send AJAX request
        jQuery.ajax({
            url: 'mailchimp/store-address.php',
            data: 'ajax=true&email=' + escape($form.find('.mailchimp_email').val()),
            success: function(msg) {
                $form.find('.response').html(msg);
            }
        });
    });
	
	//twitter
	//slide tweets
	jQuery('#tweets .twitter').bind('loaded', function(){
		jQuery(this).addClass('flexslider').find('ul').addClass('slides');
	});
	if (jQuery().tweet) {
		jQuery('.twitter').tweet({
			modpath: "./twitter_widget/ajax",
		    count: 3,
		    avatar_size: 48,
		    loading_text: 'loading twitter feed...',
		    join_text: 'auto',
		    username: 'PartnersHealth1',
		    template: "{avatar}<div class=\"tweet_right\">{time}{join}<span class=\"tweet_text\">{tweet_text}</span></div>"
		});
	}


	//mainmenu
	if (jQuery().superfish) {
		jQuery('ul.sf-menu').superfish({
			delay:       300,
			animation:   {opacity:'show'},
			animationOut: {opacity: 'hide'},
			speed:       'fast',
			disableHI:   false,
			cssArrows:   true,
			autoArrows:  true
		});
	}

		//toggle mobile menu
	jQuery('.toggle_menu').on('click', function(){
		jQuery('.toggle_menu').toggleClass('mobile-active');
		jQuery('.page_header').toggleClass('mobile-active');
	});

	jQuery('.mainmenu a').on('click', function(){
		if (!jQuery(this).hasClass('sf-with-ul')) {
			jQuery('.toggle_menu').toggleClass('mobile-active');
			jQuery('.page_header').toggleClass('mobile-active');
		}
	});
		
    
	//single page localscroll and scrollspy
	var navHeight = jQuery('.page_header').outerHeight(true);
	jQuery('body').scrollspy({
		target: '.mainmenu_wrapper',
		offset: navHeight
	});
	if (jQuery().localScroll) {
		jQuery('.mainmenu, #land').localScroll({
			duration:900,
			easing:'easeInOutQuart',
			offset: -navHeight+10
		});
	}

	////////////////////
	//header processing/
	////////////////////
		//stick header to top
			//wrap header with div for smooth sticking
	var $header = jQuery('.page_header').first();
	if ($header.length) {
		var headerHeight = $header.outerHeight();
		$header.wrap('<div class="page_header_wrapper"></div>').parent().css({height: headerHeight}); //wrap header for smooth stick and unstick
			//get offset
		var headerOffset = $header.offset().top;
		jQuery($header).affix({
			offset: {
				top: headerOffset,
				bottom: 0
			}
		});
			//if header has different height on afixed and affixed-top positions - correcting wrapper height
		jQuery($header).on('affixed-top.bs.affix', function () {
			$header.parent().css({height: $header.outerHeight()});
		});
	}

	//toTop
	if (jQuery().UItoTop) {
        jQuery().UItoTop({ easingType: 'easeOutQuart' });
    }

	//parallax
	if (jQuery().parallax) {
		jQuery('.parallax').parallax("50%", 0.02);
	}
	
    //prettyPhoto
    if (jQuery().prettyPhoto) {
	   	jQuery("a[data-gal^='prettyPhoto']").prettyPhoto({
	   		hook: 'data-gal',
			social_tools:false,
            deeplinking:false,
			theme: 'facebook' /* light_rounded / dark_rounded / light_square / dark_square / facebook / pp_default*/
	  	});
	}


   	//carousel
   	if (jQuery().carousel) {
		jQuery('.carousel').carousel();
	}

	//owl carousel
	if (jQuery().owlCarousel) {
		jQuery('.owl-carousel').each(function() {
			var $carousel = jQuery(this);
			var loop = $carousel.data('loop') ? $carousel.data('loop') : false;
			var margin = ($carousel.data('margin') || $carousel.data('margin') == 0) ? $carousel.data('margin') : 30;
			var nav = $carousel.data('nav') ? $carousel.data('nav') : false;
			var dots = $carousel.data('dots') ? $carousel.data('dots') : false;
			var themeClass = $carousel.data('themeClass') ? $carousel.data('themeClass') : 'owl-theme';
			var center = $carousel.data('center') ? $carousel.data('center') : false;
			var items = $carousel.data('items') ? $carousel.data('items') : 4;
			var autoplay = $carousel.data('autoplay') ? $carousel.data('autoplay') : false;
			var responsiveXs = $carousel.data('responsive-xs') ? $carousel.data('responsive-xs') : 1;
			var responsiveSm = $carousel.data('responsive-sm') ? $carousel.data('responsive-sm') : 2;
			var responsiveMd = $carousel.data('responsive-md') ? $carousel.data('responsive-md') : 3;
			var responsiveLg = $carousel.data('responsive-lg') ? $carousel.data('responsive-lg') : 4;
			// var responsive = $carousel.data('responsive') ? jQuery.parseJSON($carousel.data('responsive')) : {0:{items:1},767:{items:2},992:{items:2},1200:{items: 4}};

			$carousel.owlCarousel({
				items: items,
				loop: loop,
				margin: margin,
				nav: nav,
				animateOut: "fadeOut",
				animateIn: "fadeIn",
				autoplay: autoplay,
				dots: dots,
				themeClass: themeClass,
				center: center,
				responsive: {
					0:{
						items: responsiveXs
					},
					767:{
						items: responsiveSm
					},
					992:{
						items: responsiveMd
					},
					1200:{
						items: responsiveLg
					}
				},
			});
		});

	} //eof owl-carousel
	
	//comingsoon counter
	if (jQuery().countdown) {
		//today date plus month for demo purpose
		var demoDate = new Date();
		demoDate.setMonth(demoDate.getMonth()+1);
		jQuery('#comingsoon-countdown').countdown({until: demoDate});
	}


	/////////
	//shop///
	/////////
	jQuery('#toggle_shop_view').on('click', function( e ) {
		e.preventDefault();
		jQuery(this).toggleClass('grid-view');
		jQuery('#products').toggleClass('grid-view list-view');
	});
	
	//zoom image
	if (jQuery().elevateZoom) {
		jQuery('#product-image').elevateZoom({
			gallery: 'product-image-gallery',
			cursor: 'pointer', 
			galleryActiveClass: 'active', 
			responsive:true, 
			loadingIcon: 'img/AjaxLoader.gif'
		});
	}
	
	//add review button
	jQuery('.review-link').on('click', function( e ) {
		var thisLink = jQuery(this);
		var reviewTabLink = jQuery('a[href="#reviews_tab"]');
		//show tab only if it's hidden
		if (!reviewTabLink.parent().hasClass('active')) {
			reviewTabLink
				.tab('show')
				.on('shown.bs.tab', function (e) {
					jQuery(window).scrollTo(jQuery(thisLink).attr('href'), 400);
				})
		}
		jQuery(window).scrollTo(jQuery(thisLink).attr('href'), 400);
	});

	//product counter
	jQuery('.plus, .minus').on('click', function( e ) {
		var numberField = jQuery(this).parent().find('[type="number"]');
		var currentVal = numberField.val();
		var sign = jQuery(this).val();
		if (sign === '-') {
			if (currentVal > 1) {
				numberField.val(parseFloat(currentVal) - 1);
			}
		} else {
			numberField.val(parseFloat(currentVal) + 1);
		}
	});
	
	//remove product from cart
	jQuery('a.remove').on('click', function( e ) {
		e.preventDefault();
		jQuery(this).closest('tr').remove();
	});

	//price filter
	if (jQuery().slider) {
		jQuery( ".slider-range-price" ).slider({
	      range: true,
	      min: 0,
	      max: 100000,
	      values: [ 1500, 30000 ],
	      slide: function( event, ui ) {
	        	jQuery( ".slider_price_min" ).val( ui.values[ 0 ] );
	        	jQuery( ".slider_price_max" ).val( ui.values[ 1 ] );
	      }
	    });
	    jQuery( ".slider_price_min" ).val( jQuery( ".slider-range-price" ).slider( "values", 0 ) );
	    jQuery( ".slider_price_max" ).val( jQuery( ".slider-range-price" ).slider( "values", 1 ) );
	}

	//color filter 
	jQuery(".color-filters").find("a[data-background-color]").each(function() {
		jQuery(this).css({"background-color" : jQuery(this).data("background-color")});
	});

	//adding CSS classes for elements that needs different styles depending on they widht width
	//see 'plugins.js' file
	jQuery('#mainteasers .col-lg-4').addWidthClass({
		breakpoints: [500, 600]
	});


	//background image teaser
	jQuery(".bg_teaser").each(function(){
		var $teaser = jQuery(this);
		var imagePath = $teaser.find("img").first().attr("src");
		$teaser.css("background-image", "url(" + imagePath + ")");
		if (!$teaser.find('.bg_overlay').length) {
			$teaser.prepend('<div class="bg_overlay"/>');
		}
	});

	//bootstrap tab - show first tab 
	jQuery('.nav-tabs').each(function() {
		jQuery(this).find('a').first().tab('show');
	});
	jQuery('.tab-content').each(function() {
		jQuery(this).find('.tab-pane').first().addClass('fade in active');
	});

	//bootstrap collapse - show first tab 
	jQuery('.panel-group').each(function() {
		jQuery(this).find('a').first().filter('.collapsed').trigger('click');
	});

	$('.teaser_content').height($('.bg_teaser').height()-60);
}//eof documentReadyInit

//function that initiating template plugins on window.load event

function windowLoadInit() {
	//tooltip
   	if (jQuery().tooltip) {
		jQuery('[data-toggle="tooltip"]').tooltip();
	}
		
	//chart
	pieChart();

	//layerSlider
	if (jQuery().layerSlider) {
		jQuery('#layerslider').layerSlider({
			// showBarTimer: true,
			// showCircleTimer: false,
        });
	}

	//flexslider
	if (jQuery().flexslider) {
		jQuery(".mainslider .flexslider").flexslider({
			animation: "fade",
			useCSS: true,
			controlNav: false,   
			directionNav: true,
		    prevText: "",
		    nextText: "",
			smoothHeight: false,
			slideshowSpeed:10000,
			animationSpeed:600,
			start: function( slider ) {
				slider.find('.slide_description > div').children().css({'visibility': 'hidden'});
				slider.find('.flex-active-slide .slide_description > div').children().each(function(index){
				var self = jQuery(this);
				var animationClass = !self.data('animation') ? 'fadeInRight' : self.data('animation');
				setTimeout(function(){
						self.addClass("animated "+animationClass);
					}, index*200);
				});
			},
			after :function( slider ){
				slider.find('.flex-active-slide .slide_description > div').children().each(function(index){
				var self = jQuery(this);
				var animationClass = !self.data('animation') ? 'fadeInRight' : self.data('animation');
				setTimeout(function(){
						self.addClass("animated "+animationClass);
					}, index*200);
				});
			},
			end :function( slider ){
				slider.find('.slide_description > div').children().each(function() {
					jQuery(this).attr('class', '');
				});
			}
		});

		jQuery(".flexslider").flexslider({
			animation: "fade",
			useCSS: true,
			controlNav: true,   
			directionNav: false,
		    prevText: "",
		    nextText: "",
			smoothHeight: true,
			slideshowSpeed:5000,
			animationSpeed:800,
			after :function( slider ){
			}
		});
	}

	//preloader
	jQuery(".preloaderimg").fadeOut();
	jQuery(".preloader").delay(200).fadeOut("slow").delay(200, function(){
		jQuery(this).remove();
	});

	jQuery('body').scrollspy('refresh');


	
	//animation to elements on scroll
	if (jQuery().appear) {
		jQuery('.to_animate').appear();
		jQuery('.to_animate').filter(':appeared').each(function(index){
			var self = jQuery(this);
			var animationClass = !self.data('animation') ? 'fadeInUp' : self.data('animation');
			var animationDelay = !self.data('delay') ? 210 : self.data('delay');
			setTimeout(function(){
				self.addClass("animated " + animationClass);
			}, index * animationDelay);
		});

		jQuery('body').on('appear', '.to_animate', function(e, $affected ) {
			jQuery($affected).each(function(index){
				var self = jQuery(this);
				var animationClass = !self.data('animation') ? 'fadeInUp' : self.data('animation');
				var animationDelay = !self.data('delay') ? 210 : self.data('delay');
				setTimeout(function(){
					self.addClass("animated " + animationClass);
				}, index * animationDelay);
			});
		});
	}

	//counters init on scroll
	if (jQuery().appear) {
		jQuery('.counter').appear();
		jQuery('.counter').filter(':appeared').each(function(index){
			if (jQuery(this).hasClass('counted')) {
				return;
			} else {
				jQuery(this).countTo().addClass('counted');
			}
		});
		jQuery('body').on('appear', '.counter', function(e, $affected ) {
			jQuery($affected).each(function(index){
				if (jQuery(this).hasClass('counted')) {
					return;
				} else {
					jQuery(this).countTo().addClass('counted');
				}
				
			});
		});
	}

	//bootstrap animated progressbar
	if (jQuery().appear) {
		if (jQuery().progressbar) {
			jQuery('.progress .progress-bar').appear();
			jQuery('.progress .progress-bar').filter(':appeared').each(function(index){
				jQuery(this).progressbar({
			        transition_delay: 300
			    });
			});
			jQuery('body').on('appear', '.progress .progress-bar', function(e, $affected ) {
				jQuery($affected).each(function(index){
					jQuery(this).progressbar({
				        transition_delay: 300
				    });
				});
			});
			//animate progress bar inside bootstrap tab
			jQuery('a[data-toggle="tab"]').on('shown.bs.tab', function(e) {
				jQuery(jQuery(e.target).attr('href')).find('.progress .progress-bar').progressbar({
			        transition_delay: 300
			    });
			});
		}
	}


	//flickr
	// use http://idgettr.com/ to find your ID
	if (jQuery().jflickrfeed) {
		jQuery("#flickr").jflickrfeed({
			flickrbase: "http://api.flickr.com/services/feeds/",
			limit: 8,
			qstrings: {
				id: "74705142@N08"
			},
			itemTemplate: '<a href="{{image_b}}" data-gal="prettyPhoto[pp_gal]"><li><img alt="{{title}}" src="{{image_s}}" /></li></a>'
		}, function(data) {
			jQuery("#flickr a").prettyPhoto({
				hook: 'data-gal',
				theme: 'facebook'
	   		});
		});
	}
}//eof windowLoadInit

jQuery(document).ready(function() {
	documentReadyInit();
	$('li.has_children>a').addClass('noclick');
	$('.noclick').on('click',function(){
		return false;
	});

		$('#languages').change(function(){
			var id=jQuery(this).val();
			jQuery.cookie("lang", id);
			location.reload();
		})
}); //end of "document ready" event


jQuery(window).load(function(){
   	windowLoadInit();
}); //end of "window load" event

jQuery(window).resize(function(){

	jQuery('body').scrollspy('refresh');
	// $('#navbar-main').data('bs.affix').options.offset = newOffset
	var $header = jQuery('.page_header');
	if ($header.length) {
		$header.first().data('bs.affix').options.offset = $header.first().offset().top;
	}
	jQuery(".page_header_wrapper").css({height: $header.first().outerHeight()}); //editing header wrapper height for smooth stick and unstick
	
});

jQuery(window).scroll(function() {
	//circle progress bar
	pieChart();
});

// a key map of allowed keys
var allowedKeys = {
    37: 'left',
    38: 'up',
    39: 'right',
    40: 'down',
    65: 'a',
    66: 'b'
};

// the 'official' Konami Code sequence
var konamiCode = ['up', 'up', 'down', 'down', 'left', 'right', 'left', 'right', 'b', 'a'];

// a variable to remember the 'position' the user has reached so far.
var konamiCodePosition = 0;

// add keydown event listener
document.addEventListener('keydown', function(e) {
    // get the value of the key code from the key map
    var key = allowedKeys[e.keyCode];
    // get the value of the required key from the konami code
    var requiredKey = konamiCode[konamiCodePosition];

    // compare the key with the required key
    if (key == requiredKey) {

        // move to the next key in the konami code sequence
        konamiCodePosition++;

        // if the last key is reached, activate cheats
        if (konamiCodePosition == konamiCode.length) {
            activateCheats();
            konamiCodePosition = 0;
        }
    } else {
        konamiCodePosition = 0;
    }
});

function activateCheats() {
    jQuery('head').append('<link rel="stylesheet" type="text/css" href="/addons/shared_addons/themes/bootstrap/css/commode.css">');
}