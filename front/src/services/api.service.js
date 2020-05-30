import axios from 'axios';
import notificationService from './notification.service';


// todo: development
const BASE_PATH = 'http://localhost:8881';

function wrapResponse(promise) {
  return promise.then(function (response) {
    return response.data.content;
  }).catch(function (error) {
    console.error(error);
    if (error.response) {
      notificationService.emitError(`HTTP error has has occurred while executing request (${error.response.status})`);
    } else {
      notificationService.emitError('Unexpected error has occurred while executing request');
    }
    return null;
  });
}

function getProfiles() {
  return wrapResponse(axios.get(BASE_PATH + '/profiles'));
}

function getProfileProperties(profileName) {
  return wrapResponse(axios.get(BASE_PATH + '/profiles/' + profileName + '/config'));
}

function setProfileProperty(profileName, property, value) {
  const payload = {
    value
  };
  return wrapResponse(axios.post(BASE_PATH + '/profiles/' + profileName + '/config/' + property, payload));
}

function renameProfileProperty(profileName, oldName, newName) {
  const payload = {
   new_name: newName
  };
  return wrapResponse(axios.post(BASE_PATH + '/profiles/' + profileName + '/config/' + oldName + '/rename', payload));
}

  function addProfileProperty(profileName, property, value) {
  const payload = {
    name: property,
    value
  };
  return wrapResponse(axios.put(BASE_PATH + '/profiles/' + profileName + '/config', payload));
}

function moveProfileUp(profileName) {
  return wrapResponse(axios.post(BASE_PATH + '/profiles/' + profileName + '/up'));
}

function moveProfileDown(profileName) {
  return wrapResponse(axios.post(BASE_PATH + '/profiles/' + profileName + '/down'));
}

function getAllProperties() {
  return wrapResponse(axios.get(BASE_PATH + '/config'));
}

function getPropertyDetails(name, includeInactive = false) {
  return wrapResponse(axios.get(BASE_PATH + '/config/' + name, {}));
}

export default {
  getProfiles,
  getProfileProperties,
  setProfileProperty,
  renameProfileProperty,
  addProfileProperty,
  moveProfileUp,
  moveProfileDown,
  getAllProperties,
  getPropertyDetails
}
