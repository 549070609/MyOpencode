<template>
  <div>
    <h1>{{ greeting }}</h1>
    <p>Name: {{ name }}</p>
    <p>Age: {{ age }}</p>
  </div>
</template>

<script>
export default {
  data() {
    return {
      name: "Alice",
      age: 30
    };
  },
  computed: {
    greeting() {
      return `Hello, ${this.name}!`;
    }
  }
};
</script>

<style scoped>
div {
  font-family: Arial, sans-serif;
  padding: 20px;
}
</style>
