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
    if ($('.portaltype-issue').length>0 || ($('.portaltype-tracker').length>0) && /\+\+add\+\+Issue/.test(window.location.href)) {
        $('body').append(
            "<div id='automatic-linking' style='display: none'>"+
              "<h1>Automatic linking</strong></h1>"+
              "<p><strong>Issues</strong> <span class='formHelp'>This field will automatically link to other issues in this tracker when you use these formats</span></p>"+
              "<ul>"+
              "<li>#123</li>"+
              "<li>issue:123</li>"+
              "<li>ticket:123</li>"+
              "<li>bug:123</li>"+
              "</ul>"+
              "<p><strong>Repository</strong> <span class='formHelp'>This field will automatically link to the Repository set in the tracker settings when you use these formats</span></p>"+
              "<ul>"+
              "<li>r123</li>"+
              "<li>changeset:123</li>"+
              "<li>[123]</li>"+
              "</ul>"+
              "<p class='formHelp'>Note: Repositories that use alphanumeric identification numbers need at least 4 characters to correctly identify the changeset when linking.</p>"+
            "</div>");
        $("label[for='form-widgets-details'] .formHelp, label[for='form-widgets-steps'] .formHelp, #response_help").append(" This field can create Automatic Links.<a href='#automatic-linking' class='automatic-linking pat-plone-modal' data-pat-plone-modal='width: 500px'><span class='icon-contentInfo'></span></a>");
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
