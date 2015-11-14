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
}); })(jQuery);