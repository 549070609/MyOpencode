<script>
  let name = "Alice";
  let age = 30;
  
  function greet() {
    return `Hello, ${name}!`;
  }
</script>

<main>
  <h1>{greet()}</h1>
  <p>Name: {name}</p>
  <p>Age: {age}</p>
</main>

<style>
  main {
    font-family: Arial, sans-serif;
    padding: 20px;
  }
</style>
