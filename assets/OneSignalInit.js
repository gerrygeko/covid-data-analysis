var OneSignal = window.OneSignal || [];
var initConfig = {
   appId: "ead5eb43-3ae1-4e43-8dab-1cd349942ffa",
   notifyButton: {
       enable: true,
   },
   // This is needed for now for localtesting
   allowLocalhostAsSecureOrigin: true,
   subdomainName: 'http://127.0.0.1:5000'
};
OneSignal.push(function () {
    OneSignal.SERVICE_WORKER_PARAM = { scope: '/assets/' };
    OneSignal.SERVICE_WORKER_PATH = 'assets/OneSignalSDKWorker.js'
    OneSignal.SERVICE_WORKER_UPDATER_PATH = 'assets/OneSignalSDKUpdaterWorker.js'
    OneSignal.init(initConfig);
});