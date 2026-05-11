"""Hand-written supplements to the generated models.

Currently empty — cross-field validators (e.g. ``Gather.numDigits`` vs
``min/maxDigits``) are appended directly to the generated class bodies
by ``scripts/regen_models.py`` via the ``CLASS_VALIDATORS`` table, so
there is no runtime patching to apply here. The package exists so
callers can import it symbolically if future patches need a home.
"""

__all__: list[str] = []
