# UML Diagrams — Personal Finance Tracker

This document contains all 6 UML diagrams for the Personal Finance Tracker Desktop Application.

## Generated PNG Diagrams

| # | Diagram | File |
|---|---------|------|
| 1 | Use Case Diagram | `use_case_diagram.png` |
| 2 | Class Diagram | `class_diagram.png` |
| 3 | Sequence Diagram | `sequence_diagram.png` |
| 4 | Activity Diagram | `activity_diagram.png` |
| 5 | Component Diagram | `component_diagram.png` |
| 6 | Deployment Diagram | `deployment_diagram.md` (Mermaid source) |

---

## 1. Use Case Diagram

![Use Case Diagram](use_case_diagram.png)

---

## 2. Class Diagram

![Class Diagram](class_diagram.png)

---

## 3. Sequence Diagram

![Sequence Diagram](sequence_diagram.png)

---

## 4. Activity Diagram

![Activity Diagram](activity_diagram.png)

---

## 5. Component Diagram

![Component Diagram](component_diagram.png)

---

## 6. Deployment Diagram

```mermaid
graph TB
    subgraph Desktop["«device» User's Desktop Computer"]
        subgraph Python["«executionEnvironment» Python 3.10+ Runtime"]
            main["«artifact» main.py"]
            db_mod["«artifact» database.py"]
            val["«artifact» validator.py"]
            exc["«artifact» exceptions.py"]
        end

        subgraph Tkinter["«executionEnvironment» Tkinter GUI Framework"]
            tv["«artifact» transaction_view.py"]
            dv["«artifact» dashboard_view.py"]
            bv["«artifact» budget_view.py"]
        end

        subgraph SQLite["«database» SQLite Engine"]
            dbfile["«artifact» finance_tracker.db"]
        end
    end

    subgraph FS["«device» Local File System"]
        storage["«artifact» Data Storage"]
    end

    Python -- "«library»" --> Tkinter
    Python -- "«sqlite3»" --> SQLite
    main -- "«manifest»" --> tv
    main -- "«manifest»" --> dv
    main -- "«manifest»" --> bv
    SQLite -- "«local storage»" --> FS
```
