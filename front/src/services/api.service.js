import axios from 'axios';
import notificationService from './notification.service';


const BASE_PATH = 'http://localhost:8881/api';

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

function getProfileProperties(id) {
  return wrapResponse(axios.get(BASE_PATH + '/profiles/' + id + '/config'));
}

function setProfileProperty(profileId, propertyId, value) {
  const payload = {
    value
  };
  return wrapResponse(axios.post(BASE_PATH + '/profiles/' + profileId + '/config/' + propertyId, payload));
}

function renameProfileProperty(profileId, propertyId, newName) {
  const payload = {
    new_name: newName
  };
  return wrapResponse(axios.post(BASE_PATH + '/profiles/' + profileId + '/config/' + propertyId + '/rename', payload));
}

function addProfileProperty(profileId, propertyName, value) {
  const payload = {
    name: propertyName,
    value
  };
  return wrapResponse(axios.put(BASE_PATH + '/profiles/' + profileId + '/config', payload));
}

function deleteProfileProperty(profileId, propertyId) {
  return wrapResponse(axios.delete(BASE_PATH + '/profiles/' + profileId + '/config/' + propertyId));
}

function moveProfileUp(id) {
  return wrapResponse(axios.post(BASE_PATH + '/profiles/' + id + '/up'));
}

function moveProfileDown(id) {
  return wrapResponse(axios.post(BASE_PATH + '/profiles/' + id + '/down'));
}

function activateProfile(id) {
  return wrapResponse(axios.post(BASE_PATH + '/profiles/' + id + '/activate'));
}

function deactivateProfile(id) {
  return wrapResponse(axios.post(BASE_PATH + '/profiles/' + id + '/deactivate'));
}

function addProfile(profileName, active) {
  const payload = {
    name: profileName,
    active: active
  };
  return wrapResponse(axios.post(BASE_PATH + '/profiles', payload));
}

function getAllProperties(activeOnly) {
  return wrapResponse(axios.get(BASE_PATH + '/config' + (activeOnly ? "?active_only" : "")));
}

function getPropertyDetails(name, includeInactive = false) {
  return wrapResponse(axios.post(BASE_PATH + '/config/details', {name}));
}

export default {
  getProfiles,
  getProfileProperties,
  setProfileProperty,
  renameProfileProperty,
  addProfileProperty,
  deleteProfileProperty,
  moveProfileUp,
  moveProfileDown,
  activateProfile,
  deactivateProfile,
  addProfile,
  getAllProperties,
  getPropertyDetails,
}
