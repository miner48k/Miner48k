var hidWidth;
var scrollBarWidths = 40;

var getLeftPosi = function(){
    //   return jQuery('.dt-buttons').position().left;
};

var widthOfList = function(){
    var itemsWidth = 0;
    jQuery('.dt-buttons a').each(function(){
        var itemWidth = jQuery(this).outerWidth();
        itemsWidth+=itemWidth;
    });
    return itemsWidth;
};

var widthOfHidden = function(){
    return ((jQuery('.dt-button-wrap').outerWidth())-widthOfList()-getLeftPosi())-scrollBarWidths;
};

var reAdjust = function(){
    if ((jQuery('.dt-button-wrap').outerWidth()) < widthOfList()) {
        jQuery('.scroller-right').show();
    }
    else {
        jQuery('.scroller-right').hide();
    }

    if (getLeftPosi()<0) {
        jQuery('.scroller-left').show();
    }
    else {
        jQuery('.item').animate({left:"-="+getLeftPosi()+"px"},'slow');
        jQuery('.scroller-left').hide();
    }
}


jQuery(window).load(function() {
    jQuery(document).delegate('*[data-toggle="lightbox"]', 'click', function(event) {
        event.preventDefault();
        jQuery(this).ekkoLightbox();

    });

});


jQuery(window).load(function() {
 //   if(!window.location.hash) {
        loadpages();
   // }

  //  jQuery('body').on('click','.flipbook-lightbox-close',function(){ alert('c');
    //    loadpages();
   // })

    jQuery("body").keydown(function(e) {
        if(e.keyCode == 37) { // left
            jQuery('.nav-left')[0].click(); // Works too!!!
        }
        else if(e.keyCode == 39) { // right
            jQuery('.nav-right')[0].click(); // Works too!!!
        }
    });
});

function loadpages() {
    var selector = jQuery('.gallery-image'),
        z = 0;

    selector.each(function (i, el) {
        jQuery(el).css({'opacity': 0.1});
    })

    selector.each(function (i, el) {
        jQuery(this).waypoint(function () {
                if (!jQuery(el).hasClass('animated')) {

                    var cover = jQuery(el).data('file');

                    if (cover != "") {
                        jQuery('.thumb' + cover).attr('src', '/files/thumb/' + cover + '/400/400');
                        z++;
                        if (z == 7) {
                            equalheight('.gallery-image');
                            z = 0;
                        }
                    }
                    jQuery(el).addClass('animated');
                    jQuery(el).animate({
                        'opacity': 1.0
                    }, 450);
                }
            },
            {offset: '100%'})
    })

    jQuery('a[data-toggle="tab"]').on('shown.bs.tab', function (e) {
        var target = jQuery(e.target).attr("href") // activated tab
        if (target == "#mag_logos") {
            $container.isotope('masonry');
        }
    });
}


equalheight = function(container){

    var currentTallest = 0,
        currentRowStart = 0,
        rowDivs = new Array(),
        $el,
        topPosition = 0;
    jQuery(container).each(function() {

        $el = jQuery(this);
        jQuery($el).height('auto')
        topPostion = $el.position().top;

        if (currentRowStart != topPostion) {
            for (currentDiv = 0 ; currentDiv < rowDivs.length ; currentDiv++) {
                rowDivs[currentDiv].height(currentTallest);
            }
            rowDivs.length = 0; // empty the array
            currentRowStart = topPostion;
            currentTallest = $el.height();
            rowDivs.push($el);
        } else {
            rowDivs.push($el);
            currentTallest = (currentTallest < $el.height()) ? ($el.height()) : (currentTallest);
        }
        for (currentDiv = 0 ; currentDiv < rowDivs.length ; currentDiv++) {
            rowDivs[currentDiv].height(currentTallest);
        }
    });
}

jQuery(window).resize(function(){
    equalheight('.gallery-image');
});

