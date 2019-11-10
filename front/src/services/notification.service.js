const notificationListeners = {};

const NotificationService = {

  Level: Object.freeze({
    INFO: Symbol("info"),
    WARN: Symbol("warn"),
    ERROR: Symbol("error")
  }),

  /**
   * Handler signature:
   * handler(level, message, title)
   */
  registerListener(name, handler) {
    if (notificationListeners[name] != null) {
      throw `listener named ${name} has been already registered`;
    }
    if (typeof handler !== "function") {
      throw `handler for listener ${name} must be a function`;
    }

    notificationListeners[name] = handler;
  },

  unregisterListener(name) {
    delete notificationListeners[name];
  },

  emit: function (level, message, title) {
    for (let key in notificationListeners) {
      if (!notificationListeners.hasOwnProperty(key)) {
        continue;
      }
      notificationListeners[key](level, message, title);
    }
  },

  emitInfo: function (message, title) {
    this.emit(this.Level.INFO, message, title);
  },

  emitWarn: function (message, title) {
    this.emit(this.Level.WARN, message, title);
  },

  emitError: function (message, title) {
    this.emit(this.Level.ERROR, message, title);
  }
};

export default NotificationService;
