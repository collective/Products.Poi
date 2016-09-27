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

    // Add file upload to Issue edit view
    if ($('.template-edit.portaltype-issue')) {
        $.get( "@@poi_issue_uploads", function( data ) {
            $('.template-edit.portaltype-issue').find('#formfield-form-widgets-steps').after(data);
            require(['pat-registry'], function (registry) {
                registry.scan($('#formfield-form-widgets-attachments'));
            });
        });
    }

    // require(['mockup-patterns-tinymce']);

    // manually load tinymce is user is not authenticated...
    if($('body.userrole-anonymous.template-products-poi-content-issue-issue').length === 1){
      require(['tinymce'], function(){
        $('.pat-textareamimetypeselector').each(function(){
          // when using the textareamimetypeselector pattern, the textarea
          // is the previous element
          var $tinymce = $(this).prev();
          // hide the textareamimetypeselector
          $(this).hide();

          // we need an id for the tinymce instance
          var id = 1 + Math.floor(100000 * Math.random());
          $tinymce.attr('id', id);

          tinymce.init({
            selector: "#" + id,
            height: 500,
            plugins: [
              'advlist autolink lists link image charmap print preview anchor',
              'searchreplace visualblocks code fullscreen',
              'insertdatetime media table contextmenu paste code'
            ],
            toolbar: 'insertfile undo redo | styleselect | bold italic | alignleft aligncenter alignright alignjustify | bullist numlist outdent indent | link image'
          });
        });
      });
    }

}); })(jQuery);
