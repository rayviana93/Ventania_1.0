let nome = "Ray";
const anoNascimento = 1993;

nome = "Raysson";

console.log("Hello World!");
console.log(nome);

let cidade = "Zoro";
let preco = 49.90;
let estaLogado = true

let soma = 10 + 5;
let multiplicacao = 4 * 2;

let saudacao = "Ola," + nome + "!";

let idade = 18;
if (idade >= 18) {
    console.log("Acesso liberado.");
} else {
    console.log("Acesso negado.")
}

function darBoasVindas(nomeUsuario) {
    console.log("Seja bem-vindo(a), " + nomeUsuario + "!")
}

darBoasVindas("Ana")
darBoasVindas("Carlos")

const precoOriginal = 100;

let desconto = 20;
let precoFinal = precoOriginal - desconto;

if (precoFinal <= 80) {
    console.log("Compra em promoçao!");
} else {
    console.log("preco normal")
}