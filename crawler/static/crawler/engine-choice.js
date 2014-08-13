(function ($) {
  $(function () {
    $('#id_engine').on('change', function () {
      var url = decodeURIComponent($(this).attr('data-url-template')).replace(/<engine>/i, $(this).val()),
        target = $('#' + $(this).attr('data-target'));

      $.get(url).done(function (data) {
        if (data){
          target.text(data);
        }
      });
    });
  });
}).call(this, django.jQuery)