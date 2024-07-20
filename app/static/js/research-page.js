function sleep(ms = 0) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function initialize_timeline() {
  $('textarea')
    .each(function () {
      this.setAttribute(
        'style',
        'height:' + this.scrollHeight + 'px;overflow-y:hidden;',
      );
    })
    .on('input', function () {
      this.style.height = 0;
      this.style.height = this.scrollHeight + 'px';
    });

  $('#note-tab, #summary-tab').on('click', function () {
    $('textarea').each(function () {
      $(this).height(0);
      $(this).height(this.scrollHeight);
    });
  });
  // Timeline tag selection updates
  $('#tag-selector').on('change', function (e) {
    load_timeline($('#tag-selector').val());
  });
  $('span.tag').on('click', function () {
    load_timeline($(this).text());
  });
  // Summary removal
  $('.summary-remove-link').on('click', function () {
    $.get($(this).attr('data-url')).done(function (data) {
      load_timeline($('#tag-selector').val());
      reset_summary_form();
    });
  });
  // Summary update
  $('.summary-processing').each(async function () {
    var data_url = $(this).attr('data-url');
    var data_id = $(this).attr('data-id');
    var continue_processing = true;

    while (continue_processing) {
      $.get(data_url).done(function (data) {
        if ('processed_time' in data && data['processed_time']) {
          if (data_id == $('#summary-id').val()) {
            set_summary_form(data);
          }
          load_timeline($('#tag-selector').val());
          continue_processing = false;
        }
      });
      await sleep(2000);
    }
  });
  // Summary form loading
  $('.summary-card').on('click', function () {
    $.get($(this).attr('data-url')).done(function (data) {
      set_summary_form(data);
    });
  });
  // Note removal
  $('.note-remove-link').on('click', function () {
    $.get($(this).attr('data-url')).done(function (data) {
      load_timeline($('#tag-selector').val());
      reset_note_form();
    });
  });
  // Note form loading
  $('.note-card').on('click', function () {
    reset_note_form();
    $.get($(this).attr('data-url')).done(function (data) {
      $('#note-id').val(data['id']);
      $('#note-name').val(data['name']);
      $('#note-message').val(data['message']);
      $('#note-message').removeClass('note-empty').addClass('note-saved');

      $('#note-tags').empty();

      for (var tag_option of data['tags']) {
        selected = '';
        if (tag_option['active']) {
          selected = 'selected="selected"';
        }
        $('#note-tags').append(
          `<option value="${tag_option['name']}" ${selected}>${tag_option['name']}</option>`,
        );
      }
      $('#note-tags').select2({
        placeholder: 'Specify a topic tag',
        tags: true,
        allowClear: true,
      });

      $('#note-tab').tab('show');
      $('#note-message').height($('#note-message')[0].scrollHeight);
      set_active_note();
    });
  });
}

function load_timeline(tag = '') {
  $.get($('#timeline-url').val(), {
    tag: tag.toLowerCase(),
  }).done(function (html) {
    $('.timeline-wrapper').html(html);
    initialize_timeline();
    set_active_note();
    set_active_summary();
    window.scrollTo(0, 0);
  });
}

function set_summary_form(data) {
  reset_summary_form();
  $('#summary-id').val(data['id']);
  $('#summary-name').val(data['name']);
  $('#summary-prompt').val(data['prompt']);
  $('#summary-project-format').prop('checked', data['use_format']);
  $('#summary-research-depth').val(data['depth']);

  if ('processed_time' in data && data['processed_time']) {
    $('#summary-container .summary-text').html(data['summary']);
    set_summary_references(data['references']);

    $('#summary-container')
      .removeClass('summary-empty')
      .removeClass('summary-loading')
      .addClass('summary-loaded');
  } else {
    $('#summary-container')
      .removeClass('summary-loaded')
      .removeClass('summary-empty')
      .addClass('summary-loading');
  }

  $('#summary-tags').empty();

  for (var tag_option of data['tags']) {
    selected = '';
    if (tag_option['active']) {
      selected = 'selected="selected"';
    }
    $('#summary-tags').append(
      `<option value="${tag_option['name']}" ${selected}>${tag_option['name']}</option>`,
    );
  }
  $('#summary-tags').select2({
    placeholder: 'Specify a topic tag',
    tags: true,
    allowClear: true,
  });

  $('#summary-tab').tab('show');
  $('#summary-prompt').height($('#summary-prompt')[0].scrollHeight);
  set_active_summary();
}

function set_summary_references(references) {
  var html_references = '<ul class="reference-list">';
  references.forEach(function (reference) {
    var importance_class;

    if (reference['score'] > 70) {
      importance_class = 'imp-1';
    } else if (reference['score'] > 35) {
      importance_class = 'imp-2';
    } else {
      importance_class = 'imp-3';
    }

    html_references +=
      '<li class="reference align-middle w-100">' +
      '<span class="reference-importance ' +
      importance_class +
      '">' +
      reference['score'] +
      '%</span>' +
      '<span class="align-middle text-center fs-6 m-1"><i>' +
      reference['type'] +
      ':' +
      '</i></span>' +
      reference['link'] +
      '</li>';
  });
  html_references += '</ul>';
  $('#summary-container .summary-references').html(html_references);

  if (references.length > 0) {
    $('#summary-container .summary-reference-wrapper').show();
  } else {
    $('#summary-container .summary-reference-wrapper').hide();
  }

  // Note form loading
  $('.note-ref-link').on('click', function (event) {
    event.preventDefault();

    reset_note_form();

    $.get($(this).attr('href')).done(function (data) {
      $('#note-id').val(data['id']);
      $('#note-name').val(data['name']);
      $('#note-message').val(data['message']);
      $('#note-message').removeClass('note-empty').addClass('note-saved');

      $('#note-tab').tab('show');
      $('#note-message').height($('#note-message')[0].scrollHeight);
      set_active_note();
    });
  });

  // Summary form loading
  $('.summary-ref-link').on('click', function (event) {
    event.preventDefault();

    $.get($(this).attr('href')).done(function (data) {
      set_summary_form(data);
    });
  });
}

function reset_summary_form() {
  $('#summary-id').val('');
  $('#summary-name').val('');
  $('#summary-prompt').val('');
  $('#summary-project-format').prop('checked', true);
  $('#summary-research-depth').val(5);
  $('#summary-container .summary-text').html('');
  $('#summary-container .summary-references').html('');
  $('#summary-container')
    .addClass('summary-empty')
    .removeClass('summary-loading')
    .removeClass('summary-loaded');

  $('#summary-tags').empty();
  $('.doc-selector-cb').prop('checked', false);
  reset_active_summary();
  window.scrollTo(0, 0);
}

function reset_active_summary() {
  $('.summary-card').removeClass('active');
}

function set_active_summary() {
  var summary_id = $('#summary-id').val();
  reset_active_summary();
  if (summary_id) {
    $('#timeline-' + summary_id).addClass('active');
  }
  $('#main-content').each(function () {
    this.setAttribute(
      'style',
      'height:' + this.scrollHeight + 'px;overflow-y:hidden;',
    );
  });
  window.scrollTo(0, 0);
}

function reset_note_form() {
  $('#note-id').val('');
  $('#note-name').val('');
  $('#note-message').val('');
  $('#note-message').addClass('note-empty').removeClass('note-saved');

  $('#note-tags').empty();
  reset_active_note();
  window.scrollTo(0, 0);
}

function reset_active_note() {
  $('.note-card').removeClass('active');
}

async function set_active_note() {
  var note_id = $('#note-id').val();
  reset_active_note();
  if (note_id) {
    $('#timeline-' + note_id).addClass('active');
  }

  await sleep(1000);

  $('#main-content').each(function () {
    this.setAttribute(
      'style',
      'height:' + this.scrollHeight + 'px;overflow-y:hidden;',
    );
  });
  window.scrollTo(0, 0);
}

function initialize_project_modals() {
  $('#create-project-link').on('click', function (event) {
    event.preventDefault();
    $('#iframe-modal iframe').attr('src', $(this).attr('data-href'));
    $('#iframe-modal').modal('show');
    $('#iframe-modal').attr('data-reload', true);
  });
  $('#update-project-link').on('click', function (event) {
    event.preventDefault();
    $('#iframe-modal iframe').attr('src', $(this).attr('data-href'));
    $('#iframe-modal').modal('show');
    $('#iframe-modal').attr('data-reload', true);
  });

  $('#iframe-modal .close').on('click', function () {
    $('#iframe-modal').modal('hide');
    $('#iframe-modal iframe').attr('src', 'about:blank');

    if ($('#iframe-modal').attr('data-reload')) {
      location.reload();
    }
  });
}

$(function () {
  $('textarea')
    .each(function () {
      this.setAttribute(
        'style',
        'height:' + this.scrollHeight + 'px;overflow-y:hidden;',
      );
    })
    .on('input', function () {
      this.style.height = 0;
      this.style.height = this.scrollHeight + 'px';
    });

  $('#team-selector').on('change', function () {
    reset_summary_form();
    reset_note_form();
  });
  $('#project-selector').on('change', function () {
    var project = $(this).val();
    $.get($(`option#project-${project}`).attr('data-url'), function (data) {
      window.location.reload();
      reset_summary_form();
      reset_note_form();
    });
  });

  // Summary form initialization
  $('#summary-tags').select2({
    placeholder: 'Specify a topic tag',
    tags: true,
    allowClear: true,
  });

  $('#summary-name-toggle-button').on('click', function () {
    $('#summary-name').toggle();
  });

  $('a#summary-expand').on('click', function () {
    $('#summary-container').addClass('summary-expanded');
    $('#main-content').each(function () {
      this.setAttribute(
        'style',
        'height:' + this.scrollHeight + 'px;overflow-y:hidden;',
      );
    });
  });
  $('a#summary-shrink').on('click', function () {
    $('#summary-container').removeClass('summary-expanded');
    $('#main-content').each(function () {
      this.setAttribute(
        'style',
        'height:' + this.scrollHeight + 'px;overflow-y:hidden;',
      );
    });
  });

  $('.summary-reset-form-button').on('click', function () {
    reset_summary_form();
  });
  $('#summary-summarize-form-button').on('click', function () {
    $('#summary-container .summary-text').html('');
    $('#summary-container .summary-references').html('');
    $('#summary-container')
      .removeClass('summary-empty')
      .removeClass('summary-loaded')
      .addClass('summary-loading');

    var tags = [];
    $('#summary-tags option:selected').each(function () {
      tags.push($(this).val().toLowerCase());
    });

    var documents = [];
    $('.doc-selector-cb:checked').each(function () {
      documents.push($(this).val());
    });

    $.ajax({
      method: 'POST',
      url: $('#summary-save-url').val(),
      headers: {
        'X-CSRFTOKEN': $('#csrf-token').val(),
      },
      data: {
        project_id: $('#project-id').val(),
        name: $('#summary-name').val(),
        prompt: $('#summary-prompt').val(),
        use_format: $('#summary-project-format').is(':checked'),
        depth: $('#summary-research-depth').val(),
        tags: tags.join(','),
      },
    }).done(function (data) {
      if ('references' in data && data['references']) {
        set_summary_references(data['references']);
      }
      if ('summary' in data && data['summary']) {
        $('#summary-container .summary-text').html(data['summary']);
        $('#summary-container')
          .removeClass('summary-empty')
          .removeClass('summary-loading')
          .addClass('summary-loaded');
      }

      $('#summary-id').val(data['id']);
      load_timeline($('#tag-selector').val());
      set_active_summary();
    });
  });

  // Note form initialization
  $('#note-tags').select2({
    placeholder: 'Specify a topic tag',
    tags: true,
    allowClear: true,
  });

  $('a#note-expand').on('click', function () {
    $('#note-form').addClass('note-expanded');
  });
  $('a#note-shrink').on('click', function () {
    $('#note-form').removeClass('note-expanded');
  });

  $('#note-reset-form-button').on('click', function () {
    reset_note_form();
  });
  $('#note-save-form-button').on('click', function () {
    var tags = [];
    $('#note-tags option:selected').each(function () {
      tags.push($(this).val().toLowerCase());
    });

    $.ajax({
      method: 'POST',
      url: $('#note-save-url').val(),
      headers: {
        'X-CSRFTOKEN': $('#csrf-token').val(),
      },
      data: {
        note_id: $('#note-id').val(),
        project_id: $('#project-id').val(),
        name: $('#note-name').val(),
        message: $('#note-message').val(),
        tags: tags.join(','),
      },
    }).done(function (data) {
      $('#note-message').removeClass('note-empty').addClass('note-saved');

      $('#note-id').val(data['id']);
      load_timeline($('#tag-selector').val());
      set_active_note();
    });
  });

  load_timeline();
  initialize_project_modals();
});
