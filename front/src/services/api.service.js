import axios from 'axios';


// todo: development
const BASE_PATH = 'http://localhost:8881';

function wrapResponse(promise) {
  return promise.then(function (response) {
    return response.data.content;
  }).catch(function (error) {
    // TODO: error handling
    console.error(error);
    alert('Something wrong has happened, check JS log');
    return null;
  });
}

function getProfiles() {
  return wrapResponse(axios.get(BASE_PATH + '/profiles'));
}

function getProfileProperties(profileName) {
  return wrapResponse(axios.get(BASE_PATH + '/profiles/' + profileName + '/config'));
}

export default {
  getProfiles,
  getProfileProperties
}
