$(function () {
  $('.explanation-link').on('click', function (event) {
    event.preventDefault();

    $explanation = $(this).find('.explanation-popup');
    if ($explanation.length == 0) {
      $(this).append('<div class="explanation-popup"></div>');
      $explanation = $(this).find('.explanation-popup');
      $explanation.text($('#' + $(this).attr('data-ref')).text());

      $explanation.on('click', function (event) {
        event.preventDefault();
        event.stopPropagation();
        $(this).remove();
      });
    } else {
      $explanation.remove();
    }
  });
});
