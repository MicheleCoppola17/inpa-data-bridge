# inpa-data-bridge

Backend service that ingests INPA public exam data, normalizes it, stores it in PostgreSQL, and exposes REST endpoints for mobile clients.

## Stack
- Python 3.11+
- FastAPI
- SQLAlchemy 2.0 (async)
- PostgreSQL
- Alembic
- APScheduler

## Quick start

1. Create and activate a virtual environment.
2. Install dependencies:
   ```bash
   pip install -e .[dev]
   ```
3. Copy environment file:
   ```bash
   cp .env.example .env
   ```
4. Run migrations:
   ```bash
   alembic upgrade head
   ```
5. Start API:
   ```bash
   uvicorn app.main:app --reload
   ```

## Public endpoints
- `GET /api/v1/health`
- `GET /api/v1/exams`
- `GET /api/v1/exams/{id}`

Exam payloads include `short_title`, `short_description`, `sector`, `organization`, `regions`, `provinces`, `url`, `salary_range`, `selection_criteria`, `is_expired`, `published_at`, `expires_at`, `vacancies`, and `position` for cleaner presentation.

### `/api/v1/exams` query params
- `page` (default `0`)
- `size` (default `20`, max `100`)
- `is_expired` (`true|false`)
- `updated_after` (ISO datetime)
- `sector` (e.g. `Amministrativo e Contabile`)
- `region` (e.g. `Lazio`) - Matches if the region is present in the `regions` list.
- `province` (e.g. `Roma`) - Matches if the province is present in the `provinces` list.
- `q` (search over `short_title` and `description`)
- `sort` (`-published_at`, `published_at`, `-updated_at`, `updated_at`, `-expires_at`, `expires_at`)

## Internal sync endpoints
- `GET /api/v1/internal/sync/status`
- `POST /api/v1/internal/sync/run`

## INPA source endpoint
`POST https://portale.inpa.gov.it/concorsi-smart/api/concorso-public-area/search-better?page={page}&size={size}`

## Data Ingestion, Cleanup & Normalization

The ingestion pipeline retrieves exams from the official INPA endpoint, filters out unused/noisy fields, strips HTML, normalizes strings, and classifies them into structured categories for an optimal mobile reading experience.

### Mapping & Normalization Rules

| Source INPA Field | Target Schema Field | Normalization & Mapping Logic |
| :--- | :--- | :--- |
| `id` | `id`, `url` | The identifier is stored directly, and used to construct a direct link: `https://www.inpa.gov.it/bandi-e-avvisi/dettaglio-bando-avviso/?concorso_id={id}` |
| `sedi` | `regions`, `provinces` | Splits the flat list of locations. Entries matching any of the 20 official Italian regions go to `regions` (e.g. `Campania`), while others go to `provinces` (e.g. `Avellino`). |
| `entiRiferimento` | `organization` | Extracted from the first element of the references list (e.g., `Comune di Grottaminarda`). |
| `figuraRicercata` | `position`, `short_title` | The role is cleaned (removing double spaces, title-casing words, preserving known acronyms). Also used to build a readable short title. |
| `settori` / `figuraRicercata` | `sector` | Classified into predefined job sectors (e.g., `Operativo e Manutentivo`, `Amministrativo e Contabile`, `IT e Comunicazione`) based on a curated keyword dictionary. |
| `descrizioneBreve` / `descrizione` | `short_description`, `description` | Strips HTML tags and legal preambles (like *"Avviso di procedura..."*). The short description is capitalized, ends with a period, and is truncated to 160 characters. |
| `tipoProcedura` | `selection_criteria` | Translates raw codes to user-friendly criteria (e.g., `COLLOQUIO` $\to$ `Colloquio`, `TITOLI` $\to$ `Titoli`, `ESAMI` $\to$ `Esami`). |
| `dataPubblicazione` / `dataScadenza` | `published_at` / `expires_at`, `is_expired` | Parses dates to UTC datetimes. Expiration state `is_expired` is set if `expires_at < current_time`. |
| `salaryMin` / `salaryMax` | `salary_min`, `salary_max`, `salary_range` | Formats numeric bounds into a localized currency string range (e.g., `€15,328.79 - €22,993.20`). |
| `numPosti` | `vacancies` | Represents the number of available positions. |

---

### Ingestion Cleanup Example

Below is a complete transition from raw INPA API data to the cleaned, normalized database and API payload.

#### 1. Raw INPA Input JSON
```json
{
  "sedi": [
    "Campania",
    "Avellino"
  ],
  "settori": [
    "Amministrazione"
  ],
  "categorie": [
    "Avvisi di mobilità"
  ],
  "calculatedStatus": "OPEN",
  "statusLabel": "Open",
  "id": "25d33b2b4bc440eb89eae3b14be3ebbc",
  "codice": "C_E208_Mob_Obblig",
  "titolo": "AVVISO DI AVVIO PROCEDURA DI MOBILITÀ OBBLIGATORIA AI SENSI DEGLI ARTICOLI 33, 34 E 34 BIS DEL DECRETO LEGISLATIVO DEL 30 MARZO 2001, N. 165, RISERVATO ESCLUSIVAMENTE AGLI ISCRITTI NEGLI ELENCHI DEL PERSONALE IN DISPONIBILITÀ DEL CONSORZIO UNICO DI BACINO DELLE PROVINCE DI NAPOLI E CASERTA FINALIZZATO ALLA COPERTURA DI VARIE FIGURE PROFESSIONALI",
  "descrizione": "<p><span style=\"font-size: 11.0pt; font-family: 'Times New Roman',serif; mso-fareast-font-family: 'Times New Roman'; color: #000008; mso-ansi-language: IT; mso-fareast-language: EN-US; mso-bidi-language: AR-SA;\">AVVISO DI AVVIO PROCEDURA DI MOBILITÀ OBBLIGATORIA AI SENSI DEGLI ARTICOLI 33, 34 E 34 BIS DEL DECRETO LEGISLATIVO DEL 30 MARZO 2001, N. 165, RISERVATO ESCLUSIVAMENTE AGLI ISCRITTI NEGLI ELENCHI DEL PERSONALE IN DISPONIBILITÀ DEL CONSORZIO UNICO DI BACINO DELLE PROVINCE DI NAPOLI E CASERTA FINALIZZATO ALLA COPERTURA DI VARIE FIGURE PROFESSIONALI</span></p>",
  "descrizioneBreve": "<p>Avviso di Mobilità Obbligatoria riservata al personale del Consorzio Unico di Bacino della Prv. di Napoli e Caserta</p>",
  "figuraRicercata": "Operatore Esperto",
  "dataPubblicazione": "2026-03-13T13:00:00Z",
  "dataScadenza": "2026-03-28T22:59:00Z",
  "dataVisibilita": "2026-03-13T13:00:00Z",
  "linkReindirizzamento": null,
  "tipoProcedura": "COLLOQUIO",
  "group": {
    "id": null,
    "code": null,
    "concorsi": null
  },
  "importaCandidature": null,
  "options": null,
  "salaryMin": 15328.79,
  "salaryMax": 22993.2,
  "numPosti": 2,
  "status": null,
  "ente": null,
  "entiRiferimento": [
    "Comune di Grottaminarda"
  ],
  "tests": null,
  "allegatoMediaId": "f3bc1b91-b884-4d13-a7d2-2c24e582486b",
  "tipiProcedureGruppo": null,
  "numCandidaturePending": null,
  "numCandidatureSubmitted": null,
  "procedureStatusLabel": null
}
```

#### 2. Cleaned & Normalized Output API Payload (JSON)
```json
{
  "id": "25d33b2b4bc440eb89eae3b14be3ebbc",
  "regions": [
    "Campania"
  ],
  "provinces": [
    "Avellino"
  ],
  "organization": "Comune di Grottaminarda",
  "sector": "Operativo e Manutentivo",
  "short_title": "Operatore Esperto (2 posti), Comune di Grottaminarda",
  "short_description": "Di Mobilità Obbligatoria riservata al personale del Consorzio Unico di Bacino della Prv. di Napoli e Caserta.",
  "description": "AVVISO DI AVVIO PROCEDURA DI MOBILITÀ OBBLIGATORIA AI SENSI DEGLI ARTICOLI 33, 34 E 34 BIS DEL DECRETO LEGISLATIVO DEL 30 MARZO 2001, N. 165, RISERVATO ESCLUSIVAMENTE AGLI ISCRITTI NEGLI ELENCHI DEL PERSONALE IN DISPONIBILITÀ DEL CONSORZIO UNICO DI BACINO DELLE PROVINCE DI NAPOLI E CASERTA FINALIZZATO ALLA COPERTURA DI VARIE FIGURE PROFESSIONALI",
  "position": "Operatore Esperto",
  "vacancies": 2,
  "selection_criteria": [
    "Colloquio"
  ],
  "is_expired": false,
  "published_at": "2026-03-13T13:00:00+00:00",
  "expires_at": "2026-03-28T22:59:00+00:00",
  "salary_min": 15328.79,
  "salary_max": 22993.20,
  "salary_range": "€15,328.79 - €22,993.20",
  "url": "https://www.inpa.gov.it/bandi-e-avvisi/dettaglio-bando-avviso/?concorso_id=25d33b2b4bc440eb89eae3b14be3ebbc",
  "updated_at": "2026-06-30T10:44:54+00:00"
}
```

## Notes
- **Multi-Region Support**: The service correctly parses the flat `sedi` array from INPA, distinguishing between regions and provinces using a curated list of the 20 Italian regions.
- **Data Structure**: `regions` and `provinces` are stored as JSONB arrays to handle exams spanning multiple locations.
- **Filtering**: Filtering by `region` or `province` uses containment logic (matches if the requested value exists in the respective list).
- **Data Synchronization**: Ingestion uses content hashing to check for modifications. If the hash hasn't changed, the `updated_at` timestamp is preserved, preventing unnecessary app refreshes.
- **Automatic Cleanup**: Exams that have been expired for more than 14 days are automatically deleted from the database at the end of each sync run.
- **Scheduler**: Controlled via `SYNC_ENABLED` and `SYNC_CRON` environment variables.
- **Load Balancing**: The sync mechanism limits ingestion to a default maximum of 50 pages (up to 2,500 exams) per run.
