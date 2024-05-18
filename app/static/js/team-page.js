function validate_email(email) {
  if (/^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,6})+$/.test(email)) {
    return true;
  }
  return false;
}

$(function () {
  $('a.resend-link').on('click', function (event) {
    event.preventDefault();
    $.get($(this).attr('href'), function (data) {
      window.location.reload();
    });
  });
  $('#invite-email').on('keyup', function () {
    if (validate_email($(this).val())) {
      $('#invite-button').removeAttr('disabled');
      $(this).removeClass('email-invalid');
      $(this).addClass('email-valid');
    } else {
      $('#invite-button').attr('disabled', 'disabled');
      $(this).removeClass('email-valid');
      $(this).addClass('email-invalid');
    }
  });

  $('#invite-button').on('click', function () {
    var url = $('#invite-url').val();
    var email = $('#invite-email').val();

    $.get(url, { email: email }, function (data) {
      $('#invite-email').val('');
      $('#invite-button').attr('disabled', 'disabled');
      window.location.reload();
    });
  });
});
