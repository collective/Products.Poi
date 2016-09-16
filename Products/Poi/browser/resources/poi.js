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
    require(['tinymce'], function(){
        tinymce.init({
          selector: '.pat-tinymce',
          height: 500,
          plugins: [
            'advlist autolink lists link image charmap print preview anchor',
            'searchreplace visualblocks code fullscreen',
            'insertdatetime media table contextmenu paste code'
          ],
          toolbar: 'insertfile undo redo | styleselect | bold italic | alignleft aligncenter alignright alignjustify | bullist numlist outdent indent | link image'
        });
    });


}); })(jQuery);