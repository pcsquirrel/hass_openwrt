from homeassistant.config_entries import ConfigEntry
from homeassistant.components.switch import SwitchEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory

import logging

from . import OpenWrtEntity
from .constants import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities
) -> None:
    entities = []
    data = entry.as_dict()
    device = hass.data[DOMAIN]['devices'][entry.entry_id]
    device_id = data['data']['id']
    for net_id, info in device.coordinator.data['wireless'].items():
        if "wps" in info:
            sensor = WirelessWpsSwitch(device, device_id, net_id)
            entities.append(sensor)

    for redirect_id, info in device.coordinator.data["redirect"].items():
        sensor = RedirectSwitch(device, device_id, redirect_id)
        entities.append(sensor)

    for net_id, info in device.coordinator.data["radio"].items():
        sensor = WirelessRadioSwitch(device, device_id, net_id)
        entities.append(sensor)

    async_add_entities(entities)
    return True



class RedirectSwitch(OpenWrtEntity, SwitchEntity):
    def __init__(self, device, device_id, redirect_id: str):
        super().__init__(device, device_id)
        self._redirect_id = redirect_id

    @property
    def unique_id(self):
        return "%s.%s.redirect" % (super().unique_id, self._redirect_id)

    @property
    def name(self):
        return "%s Redirect [%s] toggle" % (
            super().name,
            self.data["redirect"][self._redirect_id]["name"],
        )

    @property
    def is_on(self):
        return (
            False
            if self.data["redirect"][self._redirect_id].get("enabled", True) != "1"
            else True
        )

    async def async_turn_on(self, **kwargs):
        await self._device.set_redirect(self._redirect_id, True)
        # self._device.make_async_update_data()

        # self.async_schedule_update_ha_state()
        self.data["redirect"][self._redirect_id]["enabled"] = True

    async def async_turn_off(self, **kwargs):
        await self._device.set_redirect(self._redirect_id, False)
        # self._device.make_async_update_data()
        # self.async_schedule_update_ha_state()
        self.data["redirect"][self._redirect_id]["enabled"] = False

        
class WirelessRadioSwitch(OpenWrtEntity, SwitchEntity):
    def __init__(self, device, device_id, interface: str):
        super().__init__(device, device_id)
        self._interface_id = interface

    @property
    def unique_id(self):
        return "%s.%s.RADIO" % (super().unique_id, self._interface_id)

    @property
    def name(self):
        return "%s Wireless [%s] radio toggle" % (super().name, self._interface_id)

    @property
    def is_on(self):
        return self.data["radio"][self._interface_id]["up"]

    async def async_turn_on(self, **kwargs):
        await self._device.set_radio(self._interface_id, True)
        self._device.make_async_update_data()

        # self.async_schedule_update_ha_state()
        self.data["radio"][self._interface_id]["up"] = True

    async def async_turn_off(self, **kwargs):
        await self._device.set_radio(self._interface_id, False)
        self._device.make_async_update_data()
        # self.async_schedule_update_ha_state()
        self.data["radio"][self._interface_id]["up"] = False

        

    @property
    def icon(self):
        return "mdi:security"

    @property
    def entity_category(self):
        return EntityCategory.CONFIG


class WirelessWpsSwitch(OpenWrtEntity, SwitchEntity):
    def __init__(self, device, device_id, interface: str):
        super().__init__(device, device_id)
        self._interface_id = interface

    @property
    def unique_id(self):
        return "%s.%s.wps" % (super().unique_id, self._interface_id)

    @property
    def name(self):
        return "%s Wireless [%s] WPS toggle" % (super().name, self._interface_id)

    @property
    def is_on(self):
        return self.data["wireless"][self._interface_id]["wps"]

    async def async_turn_on(self, **kwargs):
        await self._device.set_wps(self._interface_id, True)
        self.data["wireless"][self._interface_id]["wps"] = True

    async def async_turn_off(self, **kwargs):
        await self._device.set_wps(self._interface_id, False)
        self.data["wireless"][self._interface_id]["wps"] = False

    @property
    def icon(self):
        return "mdi:security"

    @property
    def entity_category(self):
        return EntityCategory.CONFIG
