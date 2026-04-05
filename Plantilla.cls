\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{plantillauft}[2025/06/11 Clase base corregida]

% Carga base article y configura tamaño de hoja
\LoadClass[a4paper,12pt]{article}

% ------------------ Paquetes ------------------

\RequirePackage[utf8]{inputenc}
\RequirePackage[T1]{fontenc}
\RequirePackage[spanish]{babel}
\RequirePackage{graphicx}
\RequirePackage{geometry}
\RequirePackage{fancyhdr}
\RequirePackage{caption}
\RequirePackage{subcaption}
\RequirePackage{float}
\RequirePackage{mathtools}
\RequirePackage{siunitx}
\RequirePackage{booktabs}
\RequirePackage{array}
\RequirePackage{url}
\RequirePackage[hidelinks]{hyperref}


\geometry{left=2.5cm,right=2.5cm,top=2cm,bottom=3.5cm}
\setlength{\headheight}{30pt}

% ------------------ Comandos personalizados ------------------

\newcommand{\titulo}[1]{\def\@titulo{#1}}
\newcommand{\prof}[1]{\def\@prof{#1}}
\newcommand{\alumnos}[1]{\def\@alumnos{#1}}
\newcommand{\ayudante}[1]{\def\@ayudante{#1}}
\newcommand{\asignatura}[1]{\def\@asignatura{#1}}

% ------------------ Encabezados ------------------

\newcommand{\fairemarges}{
  \pagestyle{fancy}
  \lhead{\includegraphics[height=1.5cm]{Facultad_de_ingenieria.png}}
  \rhead{\nouppercase{\leftmark}}

}

% ------------------ Portada ------------------

\newcommand{\portada}{
\begin{titlepage}
\thispagestyle{empty}


\noindent

\vspace{2cm}
\noindent
\includegraphics[width=0.5\linewidth]{Facultad_de_ingenieria.png} \\
\rule{\linewidth}{0.2mm} 

\begin{flushleft}
\textbf{Universidad Finis Terrae} \\
Facultad de Ingeniería \\
Asignatura: \@asignatura \\
\end{flushleft}

\vspace{2.5cm}
\begin{center}

\rule{\linewidth}{0.2mm} \\
  {\Huge \textbf{\@titulo} \par}
\rule{\linewidth}{0.2mm}  
  \vspace{4cm}

  \begin{minipage}{0.5\textwidth}
    \begin{flushleft} \large
      \textbf{Alumnos:} \\
      \@alumnos
    \end{flushleft}
  \end{minipage}
  ~
  \begin{minipage}{0.4\textwidth}
    \begin{flushright} \large
      \textbf{Profesor(a):} \\
      \@prof \\[0.2cm]

    \end{flushright}
  \end{minipage}

  \vfill
  {\large \today\par}
\end{center}
\end{titlepage}
}
