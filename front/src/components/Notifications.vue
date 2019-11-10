<template>
  <div>
    <b-alert v-for="alert in alerts" :key="alert" show fade
             :variant="alert.variant" :dismissible="alert.variant === 'danger'">{{alert.message}}</b-alert>
  </div>
</template>

<script>
  import notificationService from '../services/notification.service';

  const TIMEOUT = 10; // not applicable to error messages

  export default {
    name: 'Notifications',
    data: function () {
      return {
        alerts: []
      }
    },

    mounted() {
      notificationService.registerListener('notificationModule', (level, message, title) => {
        let variant = '';
        switch (level) {
          case notificationService.Level.INFO:
            variant = 'success';
            break;
          case notificationService.Level.WARN:
            variant = 'warning';
            break;
          case notificationService.Level.ERROR:
            variant = 'danger';
            break;
        }

        const alert = {
          variant,
          message
        };
        this.alerts.push(alert);
        if (level !== notificationService.Level.ERROR) {
          this.delayedDismiss(alert);
        }
      });
    },

    methods: {
      delayedDismiss(alert) {
        setTimeout(() => {
          const index = this.alerts.indexOf(alert);
          this.alerts.splice(index, 1);
        }, TIMEOUT * 1000);
      }
    }
  }
</script>
