"""
Energy System catalog archetype, understood as a cluster of energy systems
SPDX - License - Identifier: LGPL - 3.0 - or -later
Copyright © 2023 Concordia CERC group
Project Coder Pilar Monsalvete Alvarez de Uribarri pilar.monsalvete@concordia.ca
Code contributors: Saeed Ranjbar saeed.ranjbar@concordia.ca
"""

from typing import List

from hub.catalog_factories.data_models.energy_systems.system import System


class Archetype:
  """
  Archetype class
  """
  def __init__(self, name, systems):

    self._name = name
    self._systems = systems

  @property
  def name(self):
    """
    Get name
    :return: string
    """
    return self._name

  @property
  def systems(self) -> List[System]:
    """
    Get list of equipments that compose the total energy system
    :return: [Equipment]
    """
    return self._systems

  def to_dictionary(self):
    """Class content to dictionary"""
    _systems = []
    for _system in self.systems:
      _systems.append(_system.to_dictionary())
    content = {
      'Archetype': {
        'name': self.name,
        'systems': _systems
        }
      }
    return content
