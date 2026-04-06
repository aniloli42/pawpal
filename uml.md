classDiagram
    direction TB

    class Owner {
        +String id
        +String name
        +int available_minutes
        +int start_hour
        +List~String~ preferences
        +List~Pet~ pets
        +List~Schedule~ schedules
        +Scheduler scheduler
        +add_pet(pet: Pet) None
        +remove_pet(pet_id: String) None
        +get_pets() List~Pet~
        +get_pet(pet_id: String) Pet
        +update_pet(pet_id: String, kwargs) None
        +create_task(pet_id, title, duration_minutes, priority, category, time, notes, status, recurrence, preferred_time_slot, due_date) Task
        +remove_task(task_id: String) None
        +get_tasks(pet_id: String) List~Task~
        +get_task(task_id: String) Task
        +get_filtered_tasks(pet_id, status, sort_by) List~Task~
        +filter_tasks_by_pet_or_status(pet_name, status) List~Task~
        +update_task(task_id: String, kwargs) None
        +complete_task(task_id: String, on_date: String) None
        +build_schedule(pet_id: String, date: String) Schedule
        +get_schedules(pet_id: String) List~Schedule~
        +get_schedule(schedule_id: String) Schedule
        +remove_schedule(schedule_id: String) None
    }

    class Pet {
        +String id
        +String name
        +String species
        +String breed
        +int age
        +List~Task~ tasks
        +add_task(task: Task) None
        +remove_task(task_id: String) None
        +get_tasks() List~Task~
        +get_task(task_id: String) Task
    }

    class Task {
        +String id
        +String pet_id
        +String title
        +int duration_minutes
        +String priority
        +String category
        +String time
        +String notes
        +String status
        +String recurrence
        +String preferred_time_slot
        +String due_date
        +is_high_priority() bool
        +is_due(date: String) bool
        +set_status(status: String) None
        +mark_complete(on_date: String) None
        +to_dict() Dict
    }

    class ScheduledSlot {
        +Task task
        +int start_minute
        +int end_minute
        +time_label(start_hour: int) String
        +to_dict(start_hour: int) Dict
    }

    class Schedule {
        +String id
        +String pet_id
        +String date
        +List~Task~ scheduled_tasks
        +List~Task~ unscheduled_tasks
        +int total_duration_minutes
        +List~ScheduledSlot~ slots
        +List~String~ conflicts
        +int start_hour
        +explain() String
        +get_task(task_id: String) Task
        +to_dict() Dict
    }

    class Scheduler {
        +Dict PRIORITY_ORDER$
        +Dict SLOT_CAPACITY$
        +generate(pet: Pet, available_minutes: int, date: String, start_hour: int) Schedule
        +detect_time_conflicts(tasks: List~Task~)$ List~String~
        +sort_by_time(tasks: List~Task~)$ List~Task~
        +filter_tasks(tasks, status, sort_by)$ List~Task~
        -_sort_tasks(tasks: List~Task~) List~Task~
        -_detect_slot_conflicts(slots: List~ScheduledSlot~) List~String~
    }

    Owner "1" --> "1..*" Pet : owns
    Owner "1" --> "1" Scheduler : uses (injected via DIP)
    Owner "1" --> "0..*" Schedule : manages
    Owner ..> Task : creates/completes
    Pet "1" --> "0..*" Task : has
    Scheduler ..> Pet : reads tasks from
    Scheduler ..> Schedule : creates
    Scheduler ..> ScheduledSlot : creates
    Schedule "1" --> "0..*" ScheduledSlot : contains slots
    Schedule "1" --> "0..*" Task : includes (scheduled + unscheduled)
    ScheduledSlot "1" --> "1" Task : pins task to time window
    Task "*" ..> "1" Pet : references via pet_id