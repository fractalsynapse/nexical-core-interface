function setActiveMenu(url) {
  $('.l-navbar a').removeClass('active');
  if (url.indexOf('/teams') > -1) {
    $('#lnk-teams').addClass('active');
  } else if (url.indexOf('/projects') > -1) {
    $('#lnk-projects').addClass('active');
  } else if (url.indexOf('/documents') > -1) {
    $('#lnk-documents').addClass('active');
  } else if (url.indexOf('/research') > -1) {
    $('#lnk-research').addClass('active');
  } else if (url.indexOf('/api/docs') > -1) {
    $('#lnk-api-docs').addClass('active');
  } else if (url.indexOf('/users/update') > -1) {
    $('#lnk-profile').addClass('active');
    $('#lnk-account').addClass('active');
  } else if (url.indexOf('/accounts/email') > -1) {
    $('#lnk-emails').addClass('active');
    $('#lnk-account').addClass('active');
  } else if (url.indexOf('/accounts/password/change') > -1) {
    $('#lnk-pass').addClass('active');
    $('#lnk-account').addClass('active');
  } else if (url.indexOf('/users/token') > -1) {
    $('#lnk-token').addClass('active');
    $('#lnk-account').addClass('active');
  } else if (url.indexOf('/contact') > -1) {
    $('#lnk-contact').addClass('active');
  } else if (url.indexOf('/accounts/logout') > -1) {
    $('#lnk-logout').addClass('active');
  }
}

function checkModal() {
  $('#iframe-modal').each(function () {
    if ($(this).is(':visible')) {
      $('#outer-help').hide();
    } else {
      $('#outer-help').show();
    }
  });
}

$(function () {
  let leftNavOpen = false;
  let url = location.href;

  // Enable popper.js tooltips
  const tooltipTriggerList = document.querySelectorAll(
    '[data-bs-toggle="tooltip"]',
  );
  const tooltipList = [...tooltipTriggerList].map(
    (tooltipTriggerEl) => new bootstrap.Tooltip(tooltipTriggerEl),
  );

  setActiveMenu(url);
  window.setInterval(checkModal, 500);

  $.get($('#user-settings-url').val(), function (data) {
    $('.user-setting').each(function () {
      var userSetting = $(this).attr('data-user-setting');
      var userSettingValue = $(this).attr('data-user-value');

      if (userSetting in data && data[userSetting] == userSettingValue) {
        $(this).tab('show');
      }
    });
    $('.wait-for-load').show();
  });
  $('.user-setting').on('click', function () {
    $.ajax({
      method: 'POST',
      url: $('#user-settings-save-url').val(),
      headers: {
        'X-CSRFTOKEN': $('#csrf-token').val(),
      },
      data: {
        [$(this).attr('data-user-setting')]: $(this).attr('data-user-value'),
      },
    });
  });

  $('#team-selector').on('change', function () {
    var team = $(this).val();
    $.get($(`option#team-${team}`).attr('data-url'), function (data) {
      window.location.reload();
    });
  });

  $('.l-navbar, .l-navbar a').on('mouseover', function () {
    $('#nav-logo-icon').addClass('d-none');
    $('#nav-logo-full').removeClass('d-none');
    $('body').addClass('show-left-nav');
    leftNavOpen = true;
  });
  $('.l-navbar').on('mouseout', function () {
    $('#nav-logo-icon').removeClass('d-none');
    $('#nav-logo-full').addClass('d-none');
    $('body').removeClass('show-left-nav');
    leftNavOpen = false;
  });
  leftNavOpen = setInterval(function () {
    if (
      leftNavOpen == false &&
      $('#lnk-account').attr('aria-expanded', 'true')
    ) {
      $('#lnk-account').addClass('collapsed');
      $('#lnk-account').attr('aria-expanded', 'false');
      $('#flush-collapseAccount').removeClass('show');
    }
  }, 2000);

  // Mobile menu button
  $('#btn-menu').click(function () {
    $('body').addClass('show-left-nav');
    $('.overlay-mobile').addClass('show animate__fadeInRight');
    $('.overlay-mobile').click(function () {
      $(this).removeClass('show animate__fadeInRight');
      $('body').removeClass('show-left-nav');
    });
  });
});
