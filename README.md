## codigo-fuente
Repositorio de código donde se almacenará el trabajo realizado en frontend a lo largo de los sprints para el correcto desarrollo del proyecto.

## Politicas y estilos a seguir (Borrador)

- # Política de ramas:
  Se ha decidido seguir la siguiente política para la creación y nombrado de ramas:
* La rama principal del proyecto será la rama **main**, a la que se integrarán los cambios de la rama **develop** y de las ramas de **hotfix**, si las hubiera.
* En la rama **develop** se integrarán el resto de ramas existentes.

***

A partir de la rama **develop**:
* Por cada **Feature**, se creará una rama con la siguiente nomenclatura: **feat/nombre-de-la-funcionalidad/info-adicional-corta**.
* Por cada **Bug**, se creará al menos una rama con la siguiente nomenclatura: **bug/nombre-del-bug**.
* Por cada **Petición de Cambio**, se creará al menos una rama con la siguiente nomenclatura: **change/nombre-del-cambio**.

A partir de la rama **main**:
* Por cada **Hotfix**, se creará una rama con la siguiente nomenclatura: **hotfix/nueva-version**. Es decir, si la rama se crea sobre la versión `2.1.0` de la rama **main**, se llamará **hotfix/2.1.1**.

***

* Para integrar los cambios a la rama **main**, se hará creando pull requests desde la rama **develop** o de **hotfix**, que deberán ser revisadas y aprobadas por **al menos una persona**.
* Una vez se integre una rama de **hotfix** con la rama **main**, dicha rama será **borrada**. Acto seguido, se integrarán los cambios de la rama **main** en la rama **develop**.
* Para integrar los cambios a la rama **develop**, se hará creando pull requests desde las ramas de **feature, bug, petición de cambio o tarea de marketing**, que deberán ser revisadas y aprobadas por **al menos una persona**.
* Una vez se integre una rama de estos tipos con la rama **develop**, dicha rama será **borrada**.


- # Política de commits (estándar)
  Con respecto a la política de commits se respetará la estructura de conventional commits, de la forma:
  
  <type>[optional scope]: <description>
  [optional body]
  [optional footer(s)]

  Donde type puede ser:
  
  Para código:
  
  · `fix`: si se trata de correcciones sobre codigo ya realizado, este será el type por defecto para los commits relacionados a issues de bugs, este type puede ser usado durante el desarrollo de funcionalidades si se ha realizado una revisión o modificación de codigo ya existente, pero esta decisión es libre para cada desarrollador
  
  · `feat`: type por defecto para commits de desarrollo de caracteristicas, relacionado a la adición de codigo nuevo. Este type puede ser usado durante correciones de bugs si es necesario añadir nuevo codigo, pero esta decisión es libre para cada desarrollador
  
   · `refactor`: si se realiza alguna tarea de refactorización de código.
  
  Para documentación:
  
  · `docs`: type asociado a la creación y correccion de documentación, este type es exclusivo de la documentación y no puede aplicarse otro type para este tipo de tareas.
  
 El contenido de los commits debe intentar ser lo mas hermético posible, intentado respetar que todo el contenido de este se pueda corresponder con un solo type.

- # Estructura de versiones a seguir.
  Con respecto al versionado de las etapas del proyecto se va a utilizar un código numérico del tipo X.Y:

  · X: Representa que se han incluido cambios de forma que el sistema puede ser incompatible con versiones anteriores del mismo. Es decir, cambios que afecten en gran medida al funcionamiento y uso de la aplicación.
  
  · Y: Debe cambiarse cuando se han incluido funcionalidades nuevas pero que siguen siendo compatibles con versiones anteriores de la aplicación.

- # Propuesta de guía de estilo estándar o al menos reglas mínimas de codificación.
  Se seguira los estilos que proporciona el IDE que se usara, Visual Studio
