SESSION_GAP = 30 * 60
      

def decode_core(core) -> list[str]:
      if core is None:
            return ["UNKNOWN"]
      return getattr(core, "name", "UNKNOWN").upper()


def decode_qualifier(qualifier) -> str:
      if not qualifier:
            return ""

      if isinstance(qualifier, str):
            return qualifier.upper()

      try:
            return "|".join(
                  getattr(q, "name", str(q)).upper()
                  for q in qualifier
            )
      except TypeError:
            return str(qualifier).upper()


def add_sessions(df):
      session_ids = [0]

      for i in range(1, len(df)):
            gap = (
                  df.loc[i, "visit_time"]
                  - df.loc[i-1, "visit_time"]
            ).total_seconds()

            session_ids.append(
                  session_ids[-1] + (1 if gap > SESSION_GAP else 0)
            )

      df["session_id"] = session_ids
      return df
