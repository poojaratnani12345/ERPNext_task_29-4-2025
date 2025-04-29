const renderDependentFields = function(event) {
  const selectedValue = $(this).val();

  $("[data-atr]").each(function () {
    const $el = $(this);
    $el.hide();
    $el.find(':input').prop('disabled', true); // remove required from hidden fields
  });

  if (selectedValue) {
    const $target = $(`[data-atr='${selectedValue}']`);
    $target.show();
    $target.find(':input').prop('disabled', false); // make visible field required
  }
};



const recaptchaWidget = document.querySelector(".rc-anchor-center-item.rc-anchor-error-message");

// Hide the widget
if (recaptchaWidget) {
    recaptchaWidget.style.display = "none";
}

const formSubmitHandaler = async function(e) {
  e.preventDefault();
  const attachmentPreview = document.getElementById("attachments-preview");
  attachmentPreview.innerHTML = ""; 

  const watchFrontDialPreview = document.getElementById("watch-frontdial-preview");
    watchFrontDialPreview.innerHTML = ""; 
  const watchBackSidepreview = document.getElementById("watch-backside-preview");
    watchBackSidepreview.innerHTML = ""; 
  const invoicePreview = document.getElementById("invoice-preview");
    invoicePreview.innerHTML = "";
  const warrantyCardPreview = document.getElementById("warranty-card-preview");
    warrantyCardPreview.innerHTML = "";
  const videoPreview = document.getElementById("video-preview");
        videoPreview.innerHTML = "";

  const form = this; // this refers to the form element
  const formData = new FormData(form);

  const handleError = function(msg) {
    const errorMsg =  msg || 'Something went wrong!';
    $('#modalBody').html(`<div class="alert alert-danger">${errorMsg}</div>`);
    $('#responseModal').modal('show');
  };

  $('#loading-overlay').fadeIn();

  try {
    // 1. Execute reCAPTCHA
    // const token = await grecaptcha.enterprise.execute('6LeZeMYqAAAAAIdWfrL_TFPbnxgspxh8xFLoDIAd', {
    //   action: 'submit'
    // });

    // if (!token) {
    //   throw new Error("reCAPTCHA token could not be generated. Please try again.");
    // }

    // // 2. Verify token on backend
    // const verifyRes = await fetch("/api/method/skmei_watch.api.utils.validate_recaptcha_suport_form", {
    //   method: "POST",
    //   headers: {
    //     "Content-Type": "application/json"
    //   },
    //   body: JSON.stringify({ recaptcha_response: token })
    // });

    // const verifyResult = await verifyRes.json();
    // console.log(verifyResult);

    // if (!verifyResult.message || verifyResult.message.success === false) {
    //   throw new Error("reCAPTCHA verification failed.");
    // }

    // 3. Submit form via AJAX
    $.ajax({
      type: 'POST',
      url: $(form).attr('action'),
      data: formData,
      processData: false,  // needed for FormData
      contentType: false,  // needed for FormData
      success: function (response) {
        $('#loading-overlay').fadeOut();
        if (response.message && response.message.status === "success") {
          $('#modalBody').html(`<div class="alert alert-success">Support Ticket Created Successfully!</div>`);
          $('#responseModal').modal('show');
          form.reset(); // reset form
        } else {
          handleError(response.message?.message || "Form submission failed.");
        }
      },
      error: function (xhr) {
        $('#loading-overlay').fadeOut();
        handleError(xhr.responseJSON?.message || "Server error.");
      }
    });

  } catch (error) {
    $('#loading-overlay').fadeOut();
    handleError(error.message);
  }
};

$(()=>{
  $('#loading-overlay').fadeOut();
  renderDependentFields.call($("[name=issue_type]"));
  $("[name=issue_type]").on("change", renderDependentFields);

  $('#support-form').on('submit', formSubmitHandaler);
  
})

