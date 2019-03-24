'use strict';

const applicationServerPublicKey = 'BLXRwdEfm4jM4T-Kdinn2vGxGpcouzYMWTWx2t4U-Ejo_OGLw-9m4ShUvamPQ5pUNkckAQzemPOz5c-mzdsNjEM';

const pushButton = document.querySelector('.js-push-btn');

let isSubscribed = false;
let swRegistration = null;
let is_active;

function urlB64ToUint8Array(base64String) {
  const padding = '='.repeat((4 - base64String.length % 4) % 4);
  const base64 = (base64String + padding)
    .replace(/\-/g, '+')
    .replace(/_/g, '/');

  const rawData = window.atob(base64);
  const outputArray = new Uint8Array(rawData.length);

  for (let i = 0; i < rawData.length; ++i) {
    outputArray[i] = rawData.charCodeAt(i);
  }
  return outputArray;
}

if ('serviceWorker' in navigator && 'PushManager' in window) {
  console.log('Service Worker and Push is supported');

  navigator.serviceWorker.register('../sw.js')
  .then(function(swReg) {
    console.log('Service Worker is registered', swReg);

    swRegistration = swReg;
    initializeUI();
  })
  .catch(function(error) {
    console.error('Service Worker Error', error);
  });
} else {
  console.warn('Push messaging is not supported');
  pushButton.textContent = 'Push Not Supported';
}

function initializeUI() {
  pushButton.addEventListener('click', function() {
    pushButton.disabled = true;
    if (isSubscribed) {
    unsubscribeUser();
    } else {
      subscribeUser();
    }
  });

  // Set the initial subscription value
  swRegistration.pushManager.getSubscription()
  .then(function(subscription) {
    isSubscribed = !(subscription === null);
    is_active = isSubscribed;
    updateSubscriptionOnServer(subscription, is_active)
    if (isSubscribed) {
      console.log('User IS subscribed.');
    } else {
      console.log('User is NOT subscribed.');
    }

    updateBtn();
  });
}

function subscribeUser() {
  const applicationServerKey = urlB64ToUint8Array(applicationServerPublicKey);
  swRegistration.pushManager.subscribe({
    userVisibleOnly: true,
    applicationServerKey: applicationServerKey
  })
  .then(function(subscription) {
    console.log('User is subscribed.');
    is_active = true;
    updateSubscriptionOnServer(subscription, is_active);

    isSubscribed = true;

    updateBtn();
  })
  .catch(function(err) {
    console.log('Failed to subscribe the user: ', err);
    updateBtn();
  });
}


function updateSubscriptionOnServer(subscription, is_active) {
  // TODO: Send subscription to application server
  $.ajax({
      type: "POST",
      url: 'http://127.0.0.1:5000/api/subscribe',
      dataType: 'json',
      async: false,
      data: JSON.stringify({"subscription_info": subscription,
              "is_active": is_active })
      }).done(function(response) {
    console.log(response.data)
  }).fail(function() {
    console.log(error)
  });

  console.log(JSON.stringify(subscription));

}

function updateBtn() {
  if (Notification.permission === 'denied') {
    pushButton.textContent = 'Уведомления запрещены.';
    pushButton.disabled = true;
    return;
  }

  if (isSubscribed) {
    pushButton.textContent = 'Отключить уведомления';
  } else {
    pushButton.textContent = 'Включить уведомления';
  }

  pushButton.disabled = false;
}

function unsubscribeUser() {
  swRegistration.pushManager.getSubscription()
  .then(function(subscription) {
    if (subscription) {
      is_active = false;
      updateSubscriptionOnServer(subscription, is_active  );
      return subscription.unsubscribe();
    }
  })
  .catch(function(error) {
    console.log('Error unsubscribing', error);
  })
  .then(function() {

    

    console.log('User is unsubscribed.');
    isSubscribed = false;

    updateBtn();
  });
}