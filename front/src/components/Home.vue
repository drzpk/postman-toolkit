<template>
  <div id="home">
    <h2>Description</h2>
    <p>This website allows to define variables that can be later used in Postman. Variables are defined inside
    profiles that can be easily enabled/disabled. Each profile is ordered, so variables defined in profiles
    with higher priority will override those defined in profiles with lower priority.</p>

    <h2>Handler</h2>
    <p>The code below is the main handler that must be pasted into Postman. Follow setup instruction below
    for more information.</p>
    <prism language="javascript" :code="handlerCode"></prism>

    <h2>Setup</h2>
    <ol>
      <li>
        Define a <a href="https://learning.postman.com/docs/postman/variables-and-environments/variables/">global variable</a>
        named <span class="code">POSTMAN_TOOLKIT_URL</span> and set its value to the address of this website.
      </li>
      <li>
        Defina another global variable named <span class="code">POSTMAN_TOOLKIT_HANDLER</span> and set its value
        to the handler code above.
      </li>
      <li>
        Open a collection settings, navigate to the <i>pre-request scripts</i> section and add the code below. This
        code will act as a loader of the main handler. This way, when handler changes it won't have to be changed
        in every collection.

        <prism language="javascript" code="eval(pm.globals.get('POSTMAN_TOOLKIT_CODE'));"></prism>
      </li>
    </ol>
  </div>
</template>

<script>
  import Prism from 'vue-prismjs';
  import 'prismjs/themes/prism.css';

  import handlerCode from '../../static/postman_handler.raw.js';

  export default {
    name: 'Home',
    components: {
      Prism
    },
    data() {
      return {
        handlerCode: null
      }
    },
    mounted() {
      this.handlerCode = handlerCode
    }
  }
</script>

<style scoped>
  #home {

  }

  .code {
    background-color: #dcdbdb;
    padding: 0.15em 0.2em;
    font-family: monospace, monospace;
  }
</style>
