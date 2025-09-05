---
marp: true
---

<!-- footer: ![w:150](LDF_logo.png) -->

<style>
section {
  place-content: flex-start;
  background-color: #FAFAFA;
}


h1 {
  color: #0a5028;
}

footer {
  /* Unset default placing inherited from the built-in theme */
  left: auto;
  right: auto;
  top: auto;
  bottom: auto;

  /* Place to right-bottom */
  right: 0px;
  bottom: 0px;
}

</style>

![bg left](strom.png)
# Resistograph meets tomograph

Robert Mařík & Valentino Cristini
Mendel University in Brno

---

![bg left](strom.png)

# Content of the talk

- Resistograph and tomograph: strengths and limitations
- Combined approach: a Python library to merge data from both devices
- Vibe coding in 2025 (ChatGPT)
- Code sharing in 2025 (Docker)

---

# Tomograph

- fast and reliable tool for stem inspection
- global information from the whole cross section
- shows the size and shape of the internal defects
- cracks are reported as cavities


![bg left](tree05.png)

---

# Resistograph

- scans the power required to microdrilling at given speed
- measures mechanical properties of the material
- local information

![width:1000px](resistograph_curves.png)

---

![bg left:64% height:100%](resistograph_2D.png)

# Merge data I

- Transform resistograph data to 2D geometry of the cross section
- Visualize the data in the new geometry

---

![bg left:55% height:100%](resistograph_over_tomo.png)

# Merge data II

- merge resistograph data with tomograph data
- visualize the merged data
- look for short or long decreases in resistograph data. This indicates cracks and cavities, respectively

---

# Python library

![bg left:60% height:100%](overlays.png)

- language widely used in scientific data processing
- many libraries for data processing and visualization
- easy to automate, scale, modify, share and reuse
- easy to integrate with other tools

---

# Python library

![bg left:60% width:100%](python_code.png)

Limitations

- requires programming skills
- requires installation of Python, Python IDE and libraries
- no GUI

---

![bg left:60% ](app2.png)

# Streamlit

- library for building web apps
- requires minimal code
- interactive widgets for user input
- real-time updates
- widely used in data science and machine learning, in industry and academia

---

![bg left:60%](app2.png)

# Vibe coding

- ChatGPT 5 on August 2025
- web app in two prompts

~~~
Mam nasledujici knihovnu. Napis streamlit 
program, ktery umozni nahrat zazipovany 
adresar s daty a spusti na nem prikazy 
odpovidajici main funkci. Vystup se zobrazi.
~~~

~~~
OK. V levem panelu chci mit moznost menit 
prednastavene volby.
~~~

---

![bg left:50%](docker.png)

# Docker

A containerization platform
- packages application and its dependencies into a container
- ensures consistency across different environments
- easy to share and deploy
- widely used in industry, academia, research

---

![bg left:50%](docker.png)

# Run dockerized app

~~~
docker compose up
~~~

- 🚫 No Python install
- 🚫 No dependency issues
- 🖥️ Works on Win / Mac / Linux
- 📂 Just clone repo with `Dockerfile` and `docker-compose.yml`
- ⏳ First run = minutes, later = ms

---

![bg left](tree_python4.png)

# Summary

- Resistograph and tomograph are complementary tools for tree stem inspection
- A Python library was developed to simplify data merging and visualization
- GUI for Python is possible with Streamlit
- Installation can be made simple and repeatable with Docker

