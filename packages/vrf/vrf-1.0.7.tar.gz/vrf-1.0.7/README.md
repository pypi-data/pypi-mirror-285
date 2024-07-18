# Verifiable Random Function
VRF.py provides an implementation of a Verifiable Random Function (VRF) to ensure the randomness and fairness of a game. The script contains functions to generate seeds, proofs, and random values, and to verify the outcome of a game.


![Coverage](https://img.shields.io/badge/VRF.py-Coverage:100%25-brightgreen.svg)

## Demo


https://github.com/0xlucyy/vrf/assets/109987865/5da41a5c-52d2-40d6-81f5-0eab4480fd3c




# Table of Contents
- [Verifiable Random Function](#verifiable-random-function)
- [The Game](#the-game)
  - [generate_seed_salt_hash Function](#generate_seed_salt_hash-function)
  - [generate_beta_and_proof Function](#generate_beta_and_proof-function)
  - [Final Steps of new_game Function](#final-steps-of-new_game-function)
- [Verification](#verification)
  - [Validating the Digital Signature](#validating-the-digital-signature)
  - [Validating the Bullet Index Hash](#validating-the-bullet-index-hash)
  - [Comparison Verification](#comparison-verification)
- [TLDR](#tldr)
- [Testing](#testing)
- [Run](#run)


## The Game
Initialization of a game is achived with the `new_game` function. Belows's a detailed breakdown of the `new_game` function.

### generate_seed_salt_hash Function
The `generate_seed_salt_hash` function is a foundational step in the initialization process. It's responsible for creating a random seed and its corresponding hash. Here's a breakdown of its purpose and functionality:

- Seed Generation: The function generates a random seed using Python's `secrets.token_hex(16)`. This seed acts as a unique identifier for each game, ensuring that every game has a distinct starting point.

- Salt Generation: A random salt (`salt`) is produced using `secrets.token_hex(32)`. This salt is used in conjunction with the seed to derive the seed hash. The inclusion of a salt ensures that even if the same seed is used in multiple game rounds, the resulting seed hash will be different each time.

- Seed Hash Generation: The `seed`, combined with the `salt`, undergoes a hashing process using the `PBKDF2 HMAC SHA-512 algorithm`. This produces the `seed_hash`, which is a deterministic yet unpredictable value based on the seed and salt.

```python
  seed, seed_hash, salt = generate_seed_salt_hash()
```

### generate_beta_and_proof Function
The `generate_beta_and_proof` function is a pivotal component in the game's cryptographic operations, ensuring randomness, unpredictability, and verifiability of the game's outcome. Here's a detailed breakdown of its purpose and functionality:

- Alpha: The function takes in an `alpha` value, which is a combination of game-specific parameters; unix timestamps and player bets.

- Proof: Using randomly generated provided private key and the `alpha` value, a digital signature (`proof`) is generated. This `proof` acts as a cryptographic commitment, ensuring that the server cannot change the game's parameters without detection.

- Beta: The function calculates the `beta` value, which is derived by hashing a combination of the `seed_hash`, `salt`, and `proof`. This value is deterministic, meaning, for the same inputs, it will always produce the same output. However, due to the randomness introduced by the `seed_hash` and `salt`, it remains unpredictable for each game round.

- Bullet Index: The `beta` value is then used to determine the `bullet_index`. This index represents the starting position or the "loaded chamber" in the game, ensuring that the game's outcome is both random and verifiable.

```python
  beta, proof, bullet_index = generate_beta_and_proof(
    private_key, alpha, seed_hash, salt, revolver_chambers
  )
```

### Final Steps of new_game Function
The concluding lines of the `new_game` function solidify the game's cryptographic foundation, ensuring the game's integrity and verifiability. Here's a detailed breakdown of these operations:

- Bullet Index Hash: This step involves hashing a combination of the `bullet_index`, `salt`, and `seed_hash`. The resulting hash, termed `bullet_index_hash`, acts as a commitment to the initial state of the game. It ensures that the starting position of the bullet, along with the game's foundational parameters, remains tamper-proof.

- Public Key: The function extracts the public key from the generated private key. This public key, represented in PEM format as `public_key_pem`, will be used later for verification purposes. It ensures that any cryptographic proof provided by the server can be verified by the player.

```python
  bullet_index_hash = hashlib.pbkdf2_hmac(
    ALGO,
    (str(bullet_index) + salt + seed_hash).encode(),
    salt.encode(),
    ITERATIONS
  ).hex()

  public_key_pem = private_key.verifying_key.to_pem()
```


## Verification
The `verify` function is responsible for ensuring the integrity and authenticity of the game's outcome. It does so by validating the cryptographic proofs and commitments provided during the game's initialization. Below is a detailed breakdown of the `verify` function.

### Validating the Digital Signature
The first step in the verification process is to validate the digital signature (`proof`) against the `alpha` value using the provided `public key`. This ensures that the game's parameters have not been tampered with after the game's initialization.

- Public Key Extraction: The function begins by extracting the verifying key (`vk`) from the provided public key in PEM format.
- Signature Verification: Using the extracted verifying key, the function attempts to verify the proof against the alpha value. If the verification is successful, it confirms that the proof was indeed generated using the corresponding private key.

```python
  vk = ecdsa.VerifyingKey.from_pem(public_key)
  vk.verify(proof, alpha, hashfunc=hashlib.sha256)
```

### Validating the Bullet Index Hash
After successfully verifying the digital signature, the function proceeds to validate the bullet index hash that was provided during the game's initialization.

- Beta Calculation: The function recalculates the `beta` value by hashing a combination of the proof, salt, and seed_hash. 
- Bullet Index Determination: Using the recalculated beta value, the function derives the bullet_index. This index represents the starting position or the "loaded chamber" in the game.
- Bullet Index Hash Recalculation: The function then recalculates the hash of the bullet_index, combined with the salt and seed_hash. This derived hash should match the bullet_index_hash that was provided during the game's initialization

```python
  beta = generate_beta(proof, salt, seed_hash)
  bullet_index = int(beta, 16) % revolver_chambers
  derived_bullet_index_hash = hashlib.pbkdf2_hmac(
    ALGO,
    (str(bullet_index) + salt + seed_hash).encode(),
    salt.encode(),
    ITERATIONS
  ).hex()
```

### Comparison Verification
The final step in the validation process is to compare the recalculated bullet_index_hash with the one that was provided during the game's initialization. If they match, it confirms that the game's outcome was determined randomly and has not been altered.

```python
  if derived_bullet_index_hash == bullet_index_hash:
    return proof_validity, derived_bullet_index_hash
```


## TLDR
VRF Mechanism Breakdown:

Seed, Salt, and Seed Hash Generation:
  - A random `seed` and `salt` are generated using the secrets module.
  - A `seed hash` is then generated using the PBKDF2 HMAC algorithm with the seed and salt as inputs.

Proof Generation:
  - A `proof` is generated using the private key (sk) and an input message (`alpha`). The input message is created by concatenating the current UNIX timestamp with the array of player bets.
  - The `proof` is signed using the ECDSA algorithm with the SHA-256 hash function.

Beta Generation:
  - `Beta` is generated using the PBKDF2 HMAC algorithm with the seed hash, salt, and proof as inputs.

Bullet Index Determination:
  - The `bullet index` is determined by taking the integer representation of beta and then computing its modulo with the revolver size.

Bullet Index Hash Generation:
  - A `bullet index hash` of the bullet index is generated using the PBKDF2 HMAC algorithm with the bullet index, salt, and seed hash as inputs.

Verification:
  - A `public key` is extracted from a private key.
  - A `proof` is verified using the `public key` and an input message (`alpha`).
  - A deterministic `beta` is generated using the `proof, salt, and seed hash`.
  - The `bullet index` is derived from this beta.
  - A `derived bullet index hash` is generated using the derived bullet index, salt, and seed hash.
  - The derived bullet index hash is then compared with the bullet index hash generated during the game setup to verify the game's fairness.


## Testing
- `coverage run -m pytest tests/`
- `coverage report -m > coverage.txt`


## Run
- `git clone git@github.com:0xlucyfer/vrf.git`
- `python3 -m venv venv`
- `. venv/bin/activate`
- `pip install -r requirements.txt`
- Uncomment functions `example_run` and `main` in `vrf_py/VRF.py`.
- `python vrf_py/VRF.py`


## Install
- https://pypi.org/project/vrf/1.0.4/
- `pip install vrf==1.0.4`
- `from vrf_py import new_game, verify`


## Update Version
- `pip install --upgrade twine`
- `python setup.py sdist bdist_wheel`
- `twine upload --repository pypi dist/*`
- If prompted for token, input token from pypi found in `.pypirc` file.