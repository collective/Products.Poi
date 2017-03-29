/* global tinymce, jQuery */

(function($) { $(function() {
    // Set up overlays if Plone < 5
    try {
        $('#poi-login-form').prepOverlay({
            subtype: 'ajax',
            filter: '#content>*',
            formselector: '#content-core > form',
            noform: 'reload',
            closeselector: '[name=form.buttons.cancel]',
        });
    } catch (e) {
        // do nothing, the 'pat-plone-modal' class will display the overlay
    }

    // function to update attchments list
    function updateAttachmentsList() {
        if($('.template-poi_issue_view').length>0) {
            var path = window.location.pathname + "/@@poi_issue_uploads" + window.location.search;
        } else {
            var path = "@@poi_issue_uploads";
        }
        $.ajax({
            url: path,
            cache: false,
            success: function(data) {
                $('.issue-uploads ol').replaceWith($(data).find('ol')[0]);
            }
        });
    }

    // add file upload to Issue edit view and bind handler
    if ($('.template-edit.portaltype-issue').length>0) {
        $.get( "@@poi_issue_uploads", function( data ) {
            $('.portaltype-issue').find('.formControls').before(data);
            require(['pat-registry'], function (registry) {
                registry.scan($('#formfield-form-widgets-attachments'));
            });
            $(".template-edit.portaltype-issue .pat-upload").on('uploadAllCompleted', updateAttachmentsList);
        });
    }

    // update list after upload
    $(".template-poi_issue_view .pat-upload").on('uploadAllCompleted', updateAttachmentsList);

    // add tooltips for automatic linking
    if ($('.portaltype-issue').length>0) {
        $("label[for='form-widgets-details'] .formHelp, #response_help").append(" This field can create Automatic Links.<a href='@@poi_issue_automatic_linking' class='automatic-linking' title='test'><span class='icon-contentInfo'></span></a>");
        var bootstrapTooltip = $.fn.tooltip.noConflict();
        $(document).tooltip({
            items: '.automatic-linking',
            content: function(callback){
                $.ajax({
                    url:'@@poi_issue_automatic_linking',
                    cache: true,
                    success: function(data){
                        callback(data);
                        $('.automatic-linking').click(function (e) {
                            e.preventDefault();
                        });
                    }
                });
            }
        });
    }

    // manually load tinymce is user is not authenticated...
    if($('body.userrole-anonymous.template-products-poi-content-issue-issue').length === 1){
        require(['tinymce'], function(){
          displayEditor($("#formfield-form-widgets-details textarea"));
          displayEditor($("#formfield-form-widgets-steps textarea"));
        });
        require(['mockup-patterns-relateditems']);
    }

    // hide Fields tab in Dexterity Content Types
    $("body[class*='Tracker'].section-dexterity-types .autotoc-nav, body[class*='Issue'].section-dexterity-types .autotoc-nav").find("a:contains('Fields')").css("display", "none");


}); })(jQuery);

function displayEditor(field) {
    // we need an id for the tinymce instance
    var id = 1 + Math.floor(100000 * Math.random());
    $(field).attr('id', id);

    tinymce.init({
      selector: "#" + id,
      height: 500,
      plugins: [
        'advlist autolink lists link charmap print preview anchor',
        'searchreplace visualblocks code fullscreen',
        'insertdatetime media table contextmenu paste code'
      ],
      toolbar: 'insertfile undo redo | styleselect | bold italic | alignleft aligncenter alignright alignjustify | bullist numlist outdent indent | link'
    });
}
