function sleep(ms = 0) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function initialize_timeline() {
  $('textarea').each(function () {
    $(this).height(0);
    $(this).height(this.scrollHeight);
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
        tags: true,
        allowClear: false,
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
  });
}

function set_summary_form(data) {
  reset_summary_form();
  $('#summary-id').val(data['id']);
  $('#summary-name').val(data['name']);
  $('#summary-prompt').val(data['prompt']);

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
    tags: true,
    allowClear: false,
  });

  for (var document_id of data['documents']) {
    $('#doc-' + document_id).prop('checked', true);
  }
  $('#summary-tab').tab('show');
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
      '<li class="reference">' +
      '<span class="reference-importance ' +
      importance_class +
      '">' +
      reference['score'] +
      '%</span>' +
      '<a href="' +
      reference['link'] +
      '" target="_blank">' +
      reference['name'] +
      '</a>' +
      '</li>';
  });
  html_references += '</ul>';
  $('#summary-container .summary-references').html(html_references);
}

function reset_summary_form() {
  $('#summary-id').val('');
  $('#summary-name').val('');
  $('#summary-prompt').val('');
  $('#summary-container .summary-text').html('');
  $('#summary-container .summary-references').html('');
  $('#summary-container')
    .addClass('summary-empty')
    .removeClass('summary-loading')
    .removeClass('summary-loaded');

  $('#summary-tags').empty();
  $('.doc-selector-cb').prop('checked', false);
  reset_active_summary();
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
}

function reset_note_form() {
  $('#note-id').val('');
  $('#note-name').val('');
  $('#note-message').val('');
  $('#note-message').addClass('note-empty').removeClass('note-saved');

  $('#note-tags').empty();
  reset_active_note();
}

function reset_active_note() {
  $('.note-card').removeClass('active');
}

function set_active_note() {
  var note_id = $('#note-id').val();
  reset_active_note();
  if (note_id) {
    $('#timeline-' + note_id).addClass('active');
  }
}

$(function () {
  $('textarea').on('keyup keypress', function () {
    $(this).height(0);
    $(this).height(this.scrollHeight);
  });
  $('#note-tab, #summary-tab').on('click', function () {
    $('textarea').each(function () {
      $(this).height(0);
      $(this).height(this.scrollHeight);
    });
  });

  $('#project-selector').on('change', function () {
    var project = $(this).val();
    $.get($(`option#project-${project}`).attr('data-url'), function (data) {
      window.location.reload();
    });
  });

  // Summary form initialization
  $('#summary-tags').select2({
    tags: true,
    allowClear: false,
  });

  $('#summary-name-toggle-button').on('click', function () {
    $('#summary-name').toggle();
  });

  $('a#summary-expand').on('click', function () {
    $('#summary-container').addClass('summary-expanded');
  });
  $('a#summary-shrink').on('click', function () {
    $('#summary-container').removeClass('summary-expanded');
  });

  $('#summary-reset-form-button').on('click', function () {
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
    tags: true,
    allowClear: false,
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
});
