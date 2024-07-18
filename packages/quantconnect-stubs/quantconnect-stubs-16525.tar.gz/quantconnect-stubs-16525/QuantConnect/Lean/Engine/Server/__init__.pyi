from typing import overload
import abc

import QuantConnect.Data.UniverseSelection
import QuantConnect.Interfaces
import QuantConnect.Lean.Engine
import QuantConnect.Lean.Engine.Server
import QuantConnect.Packets
import System


class ILeanManager(System.IDisposable, metaclass=abc.ABCMeta):
    """Provides scope into Lean that is convenient for managing a lean instance"""

    def initialize(self, system_handlers: QuantConnect.Lean.Engine.LeanEngineSystemHandlers, algorithm_handlers: QuantConnect.Lean.Engine.LeanEngineAlgorithmHandlers, job: QuantConnect.Packets.AlgorithmNodePacket, algorithm_manager: QuantConnect.Lean.Engine.AlgorithmManager) -> None:
        """
        Initialize the ILeanManager implementation
        
        :param system_handlers: Exposes lean engine system handlers running LEAN
        :param algorithm_handlers: Exposes the lean algorithm handlers running lean
        :param job: The job packet representing either a live or backtest Lean instance
        :param algorithm_manager: The Algorithm manager
        """
        ...

    def on_algorithm_end(self) -> None:
        """This method is called before algorithm termination"""
        ...

    def on_algorithm_start(self) -> None:
        """This method is called after algorithm initialization"""
        ...

    def on_securities_changed(self, changes: QuantConnect.Data.UniverseSelection.SecurityChanges) -> None:
        """Callback fired each time that we add/remove securities from the data feed"""
        ...

    def set_algorithm(self, algorithm: QuantConnect.Interfaces.IAlgorithm) -> None:
        """
        Sets the IAlgorithm instance in the ILeanManager
        
        :param algorithm: The IAlgorithm instance being run
        """
        ...

    def update(self) -> None:
        """Update ILeanManager with the IAlgorithm instance"""
        ...


class LocalLeanManager(System.Object, QuantConnect.Lean.Engine.Server.ILeanManager):
    """NOP implementation of the ILeanManager interface"""

    @property
    def algorithm(self) -> QuantConnect.Interfaces.IAlgorithm:
        """
        The current algorithm
        
        This property is protected.
        """
        ...

    @property
    def system_handlers(self) -> QuantConnect.Lean.Engine.LeanEngineSystemHandlers:
        """
        The system handlers
        
        This property is protected.
        """
        ...

    @property
    def algorithm_handlers(self) -> QuantConnect.Lean.Engine.LeanEngineAlgorithmHandlers:
        """
        The algorithm handlers
        
        This property is protected.
        """
        ...

    def dispose(self) -> None:
        """Performs application-defined tasks associated with freeing, releasing, or resetting unmanaged resources."""
        ...

    def initialize(self, system_handlers: QuantConnect.Lean.Engine.LeanEngineSystemHandlers, algorithm_handlers: QuantConnect.Lean.Engine.LeanEngineAlgorithmHandlers, job: QuantConnect.Packets.AlgorithmNodePacket, algorithm_manager: QuantConnect.Lean.Engine.AlgorithmManager) -> None:
        """
        Empty implementation of the ILeanManager interface
        
        :param system_handlers: Exposes lean engine system handlers running LEAN
        :param algorithm_handlers: Exposes the lean algorithm handlers running lean
        :param job: The job packet representing either a live or backtest Lean instance
        :param algorithm_manager: The Algorithm manager
        """
        ...

    def on_algorithm_end(self) -> None:
        """This method is called before algorithm termination"""
        ...

    def on_algorithm_start(self) -> None:
        """This method is called after algorithm initialization"""
        ...

    def on_securities_changed(self, changes: QuantConnect.Data.UniverseSelection.SecurityChanges) -> None:
        """Callback fired each time that we add/remove securities from the data feed"""
        ...

    def set_algorithm(self, algorithm: QuantConnect.Interfaces.IAlgorithm) -> None:
        """
        Sets the IAlgorithm instance in the ILeanManager
        
        :param algorithm: The IAlgorithm instance being run
        """
        ...

    def update(self) -> None:
        """Execute the commands using the IAlgorithm instance"""
        ...


