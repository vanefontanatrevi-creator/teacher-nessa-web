# Teacher Nessa: publicar y editar sin código

## Preparado
La web conserva el estilo rosa/amarillo y las **163 fichas descriptivas**. Incluye recursos de creación nueva, sin páginas de libros ni datos de menores, para que haya descargas reales desde el primer día.

## Paso 1 · GitHub
Crea un repositorio en GitHub para Teacher Nessa. Sube los archivos de este ZIP manteniendo las carpetas. No subas el ZIP como un único archivo: hay que subir su contenido.

## Paso 2 · Publicación automática
En GitHub: **Settings → Pages → Build and deployment → GitHub Actions**. Abre la pestaña Actions y comprueba el flujo «Publicar Teacher Nessa». El archivo `.github/workflows/publicar.yml` ya está preparado.

## Paso 3 · Panel visual
Abre **https://app.pagescms.org/**, entra con tu cuenta de GitHub y concede permiso a ese repositorio. Pages CMS reconocerá `.pages.yml`, con dos áreas: «Biblioteca de materiales» y «Textos y apariencia».

- En «Biblioteca» puedes cambiar un título, añadir una ficha, eliminarla u ocultarla (campo «Mostrar ficha en la web»).
- Puedes elegir curso y bloque, cambiar la descripción, añadir una imagen y adjuntar documentos, vídeos o canciones.
- El archivo solo se ofrecerá como descarga cuando actives «Permitir descarga» y hayas confirmado revisión de derechos y privacidad, y siempre que sea un archivo válido subido al sitio.
- Cada cambio guardado en Pages CMS actualiza el repositorio y provoca una nueva publicación automática.

## Paso 4 · Dominio teachernessa.es
La web no estará en ese dominio hasta que lo tengas registrado y configures DNS. En GitHub Pages se puede usar un dominio propio con HTTPS.

1. Comprueba la disponibilidad/propiedad de **teachernessa.es** con un proveedor de dominios.
2. En GitHub: **Settings → Pages → Custom domain**, indica `teachernessa.es`.
3. En el proveedor de DNS, configura el dominio siguiendo la tabla vigente de GitHub. Para un dominio raíz suele usarse el conjunto de registros A que indica GitHub; configura también `www` si quieres.
4. Espera la propagación y habilita **Enforce HTTPS**.

Documentación oficial: https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site/managing-a-custom-domain-for-your-github-pages-site

## Derechos de autor y privacidad
El uso educativo y la mención de inteligencia artificial **no otorgan por sí mismos permiso para publicar contenidos de terceros**. Mantén los libros de texto, fotos de alumnos y documentos de Tutoría interna fuera de la web pública.

**Atención:** un archivo que subas a un repositorio público será público **aunque ocultes su ficha**. Revisa siempre ANTES de subir.

## Edición sin conexión
Puedes consultar `_site/index.html` directamente en un navegador. Sin GitHub no puedes guardar cambios del panel editorial, pero siempre puedes modificar los JSON en `content/` y ejecutar `python3 scripts/compilar.py`.

## Comprobar materiales disponibles
`_site/datos/estado.json` indica cuántos recursos están publicados y cuántas descargas reales hay.
