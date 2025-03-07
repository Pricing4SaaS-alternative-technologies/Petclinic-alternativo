## codigo-fuente
Repositorio de código donde se almacenará el trabajo realizado en frontend a lo largo de los sprints para el correcto desarrollo del proyecto.

## Politicas y estilos a seguir (Borrador)

- # Política de ramas:
  En el proyecto se ha establecido la siguiente politica de ramas:
  - Rama `main`: Rama principal, a esta rama solo se subiran cambios desde `develop` ya probados y funcionales, será a partir de esta rama desde la que se realizarán el resto de ramas.
    
  - Rama `develop`: Rama de integración de caracteristicas y resolución de bugs, aqui se realizarán las correcciones o posibles bugs encontrados tras cerrar el ciclo de vida de las ramas `feature`.
    
  - Ramas `feature` o `caracteristica` (pendiente de decisión): Estas ramas serán creadas para cada issue de tipo caracteristica (aquellas que comienzan con feat:...) desde `main`. En ellas se realizará el desarrollo. Tras finalizar con la caracteristica, se realizará una pull request hacia `develop`, y en caso de que no se encuentren problemas o bugs durnte el proceso de revisión, se implementarán los cambios a esta y se procederá con el borrado de la rama caracteristica pertinente.


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
