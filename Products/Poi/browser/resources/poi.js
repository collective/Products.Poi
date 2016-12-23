jQuery(function($) {
  'use strict';
  // Set up overlays
  $('#poi-login-form').prepOverlay({
    subtype: 'ajax',
    filter: '#content>*',
    formselector: '#content-core > form',
    noform: 'reload',
    closeselector: '[name="form.buttons.cancel"]',
  });
});
